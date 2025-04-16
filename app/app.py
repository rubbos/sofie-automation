from flask import Flask, render_template, request
import pandas as pd
from extractors.tax_form import main as tax_form_main
from extractors.application_form import main as application_form_main
from extractors.extra_info import main as extra_info_main
from utils.reports import (
    create_main_report,
    create_email_report,
    extracted_data,
)
import utils.validation
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

tax_form_data = pd.DataFrame()
application_form_data = pd.DataFrame()
extra_info_data = pd.DataFrame()

# Skip the upload with DEV_MODE
DEV_MODE = True
LOCAL_FILE1 = "temp_files/tax_form.txt"
LOCAL_FILE2 = "temp_files/application_form.txt"

# Register all functions from validation as globals
for func_name in dir(utils.validation):
    func = getattr(utils.validation, func_name)
    if callable(func):
        app.jinja_env.globals[func_name] = func

@app.route("/", methods=["GET", "POST"])
def upload_files():
    """Upload files and process them. Skip if in DEV_MODE."""
    global tax_form_data, application_form_data, extra_info_data
    if request.method == "POST" or DEV_MODE:
        if DEV_MODE:
            with open(LOCAL_FILE1, "r") as file1, open(LOCAL_FILE2, "r") as file2:
                tax_form_data = tax_form_main(str(file1.read()), dev_mode=True)
                application_form_data = application_form_main(
                    str(file2.read()), dev_mode=True
                )
        else:
            file1 = request.files["file1"].read()
            file2 = request.files["file2"].read()
            tax_form_data = tax_form_main(file1)
            application_form_data = application_form_main(file2)

        extra_info_data = extra_info_main()

        # Check data manually for validity before submitting
        return render_template(
            "results.html",
            extra_info_data=extra_info_data,
            tax_form_data=tax_form_data,
            application_form_data=application_form_data,
        )

    return render_template("upload.html")

@app.route("/submit-results", methods=["POST"])
def submit_results():
    """Submit the results and show the final report."""	
    tax_form_edited = get_edited_values(tax_form_data, "data_tax")
    application_form_edited = get_edited_values(
        application_form_data, "data_app")
    extra_info_edited = get_edited_values(extra_info_data, "data_extra")

    worker_info, employer_info, contract_info, calculation_info = extracted_data(
        tax_form_edited,
        application_form_edited,
        extra_info_edited,
    )
    main_report = create_main_report(
        worker_info, employer_info, contract_info, calculation_info
    )
    email_report = create_email_report(
        worker_info, employer_info, contract_info, calculation_info
    )

    return render_template(
        "final.html",
        extra_info_data=extra_info_edited,
        tax_form_data=tax_form_edited,
        application_form_data=application_form_edited,
        main_report=main_report,
        email_report=email_report,
    )


def get_edited_values(data: pd.DataFrame, key_name: str):
    """Gets the user-edited values from the form and updates the DataFrame."""

    for i in range(len(data)):
        base_key = f"{key_name}_{i}"

        # Check if row has multiple related values
        if f"{base_key}_location_start_date_1" in request.form:
            locations = []
            index = 1
            while f"{base_key}_location_start_date_{index}" in request.form:
                location_entry = [
                    request.form.get(
                        f"{base_key}_location_start_date_{index}", "").strip(),
                    request.form.get(
                        f"{base_key}_location_end_date_{index}", "").strip(),
                    request.form.get(f"{base_key}_city_{index}", "").strip(),
                    request.form.get(
                        f"{base_key}_location_country_{index}", "").strip(),
                ]
                locations.append(location_entry)
                index += 1
            data.at[i, "VALUE"] = locations

        # Handle single value updates
        else:
            key = f"{base_key}_VALUE"
            if key in request.form:
                new_value = request.form[key].strip()
                data.at[i, "VALUE"] = new_value

    return data


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
