import pandas as pd


def create_main_report(df: pd.DataFrame, df2: pd.DataFrame) -> str:
    with open("temp_files/report.txt", "r") as file:
        report = file.read()

    arrival_date = df.loc[df["KEY"] == "Arrival date", "VALUE"].values[0]
    report = report.replace("&lt;datum aankomst NL&gt;", arrival_date)

    return report


def create_email_report(df: pd.DataFrame, df2: pd.DataFrame) -> str:
    with open("temp_files/email.txt", "r") as file:
        report = file.read()

    name = df.loc[df["KEY"] == "Full name", "VALUE"].values[0]
    report = report.replace("{name}", name)

    bsn = df2.loc[df2["KEY"] == "BSN number", "VALUE"].values[0]
    report = report.replace("{bsn}", bsn)

    date_of_birth = df2.loc[df2["KEY"] == "Date of birth", "VALUE"].values[0]
    report = report.replace("{birth}", date_of_birth)

    employer = df2.loc[df2["KEY"] == "Name employer", "VALUE"].values[0]
    report = report.replace("{employer}", employer)

    loonheffing = df2.loc[df2["KEY"] == "Loonheffing number", "VALUE"].values[0]
    report = report.replace("{lhm}", loonheffing)

    # start_date_30 = df.loc[df["KEY"] == "Loonheffing number", "VALUE"].values[0]
    # report = report.replace("{start_date}", start_date_30)

    # end_date_30 = df.loc[df["KEY"] == "Loonheffing number", "VALUE"].values[0]
    # report = report.replace("{end_date}", end_date_30)

    job_name = df2.loc[df2["KEY"] == "Job title", "VALUE"].values[0]
    report = report.replace("{job_name}", job_name)

    # salarynorm = df.loc[df["KEY"] == "", "VALUE"].values[0]
    # report = report.replace("{salarynorm}", salarynorm)

    return report
