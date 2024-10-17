from flask import Flask, render_template, request
import pandas as pd
from extractors.tax_form import main as tax_form_main
from extractors.application_form import main as application_form_main
from extractors.extra_info import main as extra_info_main
from utils.validation import validate_df
from utils.reports import create_main_report, create_email_report
from utils.calculations import create_special_values
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Global variables to store dataframes
tax_form_data = pd.DataFrame()
application_form_data = pd.DataFrame()

# Skip the upload with DEV_MODE
DEV_MODE = True
LOCAL_FILE1 = "temp_files/tax_form.txt"
LOCAL_FILE2 = "temp_files/application_form.txt"


@app.route("/", methods=["GET", "POST"])
def upload_files():
    global tax_form_data, application_form_data
    if request.method == "POST" or DEV_MODE:
        if DEV_MODE:
            with open(LOCAL_FILE1, "r") as f1, open(LOCAL_FILE2, "r") as f2:
                pdf_text1 = f1.read()
                pdf_text2 = f2.read()
                tax_form_data, tax_form_data_special = tax_form_main(
                    str(pdf_text1), dev_mode=True
                )
                application_form_data = application_form_main(
                    str(pdf_text2), dev_mode=True
                )
        else:
            file1 = request.files["file1"]
            file2 = request.files["file2"]
            pdf_bytes1 = file1.read()
            pdf_bytes2 = file2.read()
            tax_form_data, tax_form_data_special = tax_form_main(pdf_bytes1)
            application_form_data = application_form_main(pdf_bytes2)

        extra_info = extra_info_main()

        extra_info_dict = extra_info.to_dict(orient="records")
        tax_form_dict = tax_form_data.to_dict(orient="records")
        application_form_dict = application_form_data.to_dict(orient="records")

        return render_template(
            "results.html",
            extra_info_data=extra_info_dict,
            tax_form_data=tax_form_dict,
            application_form_data=application_form_dict,
        )

    return render_template("upload.html")


@app.route("/submit-results", methods=["POST"])
def submit_results():
    for i in range(len(tax_form_data)):
        key = f"data_tax_{i}_VALUE"
        if key in request.form:
            new_value = request.form[key].strip()
            tax_form_data.at[i, "VALUE"] = new_value

    for i in range(len(application_form_data)):
        key = f"data_app_{i}_VALUE"
        if key in request.form:
            new_value = request.form[key].strip()
            application_form_data.at[i, "VALUE"] = new_value

    main_report = create_main_report(tax_form_data, application_form_data)
    email_report = create_email_report(tax_form_data, application_form_data)

    return render_template(
        "final.html",
        tax_form_data=tax_form_data.to_dict(orient="records"),
        application_form_data=application_form_data.to_dict(orient="records"),
        main_report=main_report,
        email_report=email_report,
    )


if __name__ == "__main__":
    app.run(debug=True)
