import pandas as pd


def create_main_report(df: pd.DataFrame, df2: pd.DataFrame) -> str:
    with open("temp_files/report.txt", "r") as file:
        report = file.read()

    employer = df2.loc[df2["KEY"] == "Name employer", "VALUE"].values[0]
    report = report.replace("[naam werkgever]", employer)
    report = report.replace("&lt;naam werkgever&gt;", employer)

    start_date = df2.loc[df2["KEY"] == "Date of entry into service", "VALUE"].values[0]
    report = report.replace("&lt;datum aanvang dienstbetrekking&gt;", start_date)
    report = report.replace("&lt;datum indiensttreding&gt;", start_date)
    report = report.replace("&lt;datum aanvang tewerkstelling&gt;", start_date)

    arrival_date = df.loc[df["KEY"] == "Arrival date", "VALUE"].values[0]
    report = report.replace("&lt;datum aankomst NL&gt;", arrival_date)
    report = report.replace("&lt;datum kwalificatie als werknemer&gt;", arrival_date)
    report = report.replace("&lt;datum eerste werkdag in Nederland&gt;", arrival_date)

    job_name = df2.loc[df2["KEY"] == "Job title", "VALUE"].values[0]
    report = report.replace("&lt;naam functie&gt;", job_name)
    ufo_code = df2.loc[df2["KEY"] == "UFO code", "VALUE"].values[0]
    report = report.replace("&lt;eventueel functiecode vermelden&gt;", f"({ufo_code})")

    # signed = df.loc[df["KEY"] == "Arrival date", "VALUE"].values[0]
    # report = report.replace("ADD SIGNED DATE ON AO", signed)

    # wilsovereenkomst

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
