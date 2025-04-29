# SOFIE Automation

SOFIE Automation is a tool that extracts text and data from specific PDF files and generates a complete report based on the extracted information.

## Why?
This is mostly related to my job, where I have to manually review files and build a complete report about an applicant. This is very repetitive work, and I figured out there is a specific pattern I follow when reviewing files and building the report. I converted this into mostly Python code. 

## Is it useful?
Yes! This improved efficiency per report from about 20-30 minutes to less than 5 minutes. This also generates fewer errors than doing it manually. You also need less knowledge about the specific laws and rules as its done all by the tool itself. 

## Features
- Most of the data is prefilled in the form. 
- Manually review and adjust the prefilled data where necessary
- Calculates all necessary data for the report with a single click.
- Includes a map of locations and a timeline of the applicant's history.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/rubbos/sofie-automation.git
    cd sofie-automation
    ```
2. Start the application using Docker.
   ```bash
    docker compose up
    ```
## Usage
1. Run the Python file:
    ```bash
    python3.12 app/app.py
    ```
2. Access the tool through your browser on 'http://localhost:5000'
2. Upload the 2 specific PDF files.
3. Double-check the prefilled data in the form. 
4. Submit the form.
3. Enjoy the completed report.

## Disclaimer
This software is provided "as is", without warranty of any kind, express or implied. Use of this tool is at your own risk. The author is not responsible for any damages, data loss, or legal issues that may result from the use of this software.

## Privacy
All data uploaded and processed by this tool remains local to your machine. No data is stored, transmitted, or shared externally.

## License
All rights reserved. This project is not licensed for redistribution, modification, or commercial use without explicit permission from the author.
