from flask import Flask, render_template, request
import pandas as pd
from extractors.main import extract_data_from_pdf

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST":
        file1 = request.files["file1"]
        file2 = request.files["file2"]

        pdf_bytes1 = file1.read()
        pdf_bytes2 = file2.read()

        data1 = extract_data_from_pdf(pdf_bytes1, method="file1")  # Method for file 1
        data2 = extract_data_from_pdf(pdf_bytes2, method="file2")  # Method for file 2

        # Convert DataFrames to lists of dictionaries
        data1_dict = (
            data1.to_dict(orient="records")
            if isinstance(data1, pd.DataFrame)
            else data1
        )
        data2_dict = (
            data2.to_dict(orient="records")
            if isinstance(data2, pd.DataFrame)
            else data2
        )

        return render_template("results.html", data1=data1_dict, data2=data2_dict)

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)  # Ensure debug mode is enabled for development
