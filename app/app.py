from flask import Flask, render_template, request
import pandas as pd
from extractors.tax_form import main as tax_form_main
from extractors.application_form import main as application_form_main

app = Flask(__name__)

# Skip the upload with DEV_MODE
# Make sure you run DEV_MODE=False once for the temp files
DEV_MODE = True
LOCAL_FILE1 = "extractors/data/tax_form.txt"
LOCAL_FILE2 = "extractors/data/application_form.txt"


@app.route("/", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST" or DEV_MODE:
        if DEV_MODE:
            with open(LOCAL_FILE1, "r") as f1, open(LOCAL_FILE2, "r") as f2:
                pdf_text1 = f1.read()
                pdf_text2 = f2.read()

                data1, data11 = tax_form_main(str(pdf_text1), dev_mode=True)
                data2 = application_form_main(str(pdf_text2), dev_mode=True)
        else:
            file1 = request.files["file1"]
            file2 = request.files["file2"]

            pdf_bytes1 = file1.read()
            pdf_bytes2 = file2.read()

            data1, data11 = tax_form_main(pdf_bytes1)
            data2 = application_form_main(pdf_bytes2)

        data1_dict = (
            data1.to_dict(orient="records")
            if isinstance(data1, pd.DataFrame)
            else data1
        )
        data11_dict = (
            data11.to_dict(orient="records")
            if isinstance(data11, pd.DataFrame)
            else data11
        )
        data2_dict = (
            data2.to_dict(orient="records")
            if isinstance(data2, pd.DataFrame)
            else data2
        )

        return render_template(
            "results.html", data1=data1_dict, data11=data11_dict, data2=data2_dict
        )

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)
