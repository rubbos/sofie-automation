from flask import Flask, render_template, request
import pandas as pd
from extractors.tax_form import main as tax_form_main
from extractors.application_form import main as application_form_main
from utils.validation import validate_df

app = Flask(__name__)

# Skip the upload with DEV_MODE
# Make sure you run DEV_MODE=False once for the temp files
DEV_MODE = True
LOCAL_FILE1 = "temp_files/tax_form.txt"
LOCAL_FILE2 = "temp_files/application_form.txt"


@app.route("/", methods=["GET", "POST"])
def upload_files():
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

        checks = validate_df(tax_form_data, application_form_data)

        tax_form_dict = (
            tax_form_data.to_dict(orient="records")
            if isinstance(tax_form_data, pd.DataFrame)
            else tax_form_data
        )
        tax_form_dict_special = (
            tax_form_data_special.to_dict(orient="records")
            if isinstance(tax_form_data_special, pd.DataFrame)
            else tax_form_data_special
        )
        checks = (
            checks.to_dict(orient="records")
            if isinstance(checks, pd.DataFrame)
            else checks
        )
        application_form_dict = (
            application_form_data.to_dict(orient="records")
            if isinstance(application_form_data, pd.DataFrame)
            else application_form_data
        )

        return render_template(
            "results.html",
            checks=checks,
            tax_form_data=tax_form_dict,
            tax_form_data_special=tax_form_dict_special,
            application_form_data=application_form_dict,
        )

    return render_template("upload.html")


if __name__ == "__main__":
    app.run()
