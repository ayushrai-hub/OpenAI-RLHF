import os
import datetime
from datetime import timedelta
from elasticsearch import Elasticsearch
import urllib3
from decouple import config
from . import config

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import pytz  # Import pytz to manage time zones

# Load settings from environment variables or a config file
es_host = config('ES_HOST')
es_port = config('ES_PORT')
es_user = config('ES_USER')
es_password = config('ES_PASSWORD')

# Additional Elasticsearch settings for SSL
es_use_ssl = config('ES_USE_SSL', default="true").lower() == "true"
verify_certs = config('ES_VERIFY_CERTS', default="false").lower() == "true"
ca_certs = config('ES_CA_CERTS', default=None)

# Email server info
sender_email = config('SENDER_EMAIL')
recipient_email = config('RECEIVERS').split(';')
ccadd_email = config('CCADDR')
smtp_server_ip = config('SMTP_SERVER_IP')
smtp_port = config('SMTP_PORT')
email_subject = 'MyGL app report-GA-2024 updates'

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Turn off SSL and certificate checking for Elasticsearch
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_es_client():
    es_options = {
        'hosts': [f"{'https' if es_use_ssl else 'http'}://{es_host}:{es_port}"],
        'http_auth': (es_user, es_password),
        'verify_certs': verify_certs,
    }
    return Elasticsearch(**es_options)

def get_local_time_in_utc(local_time: datetime.datetime, local_tz: str) -> datetime.datetime:
    """
    Converts a naive local datetime to an aware UTC datetime.
    """
    tz = pytz.timezone(local_tz)
    local_dt = tz.localize(local_time)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt

def send_email_with_attachment(csv_filename, graph_filename):
    try:
        msg = MIMEMultipart("related")
        msg["From"] = sender_email
        msg["To"] = ";".join(recipient_email)
        msg['Cc'] = ccadd_email
        msg["Subject"] = email_subject

        # HTML content with included image
        html_content = f"""
        <html>
            <body>
                <p>Dear Team,</p>
                <p>Attached is the MyGL APP report-GA-2024 update for the past four days, please review when possible.</p>
                <p>This is an automated message, no reply needed.</p>
                <img src="cid:graph_image">
                <br><br>
                <p>Sincerely,</p>
                <p>App Monitoring Team</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))

        # Add CSV file
        with open(csv_filename, "rb") as csv_file:
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(csv_file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(csv_filename)}"')
            msg.attach(attachment)

        # Add Graph image and embed in email content
        with open(graph_filename, "rb") as graph_file:
            img = MIMEImage(graph_file.read(), name=os.path.basename(graph_filename))
            img.add_header('Content-ID', '<graph_image>')
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(graph_filename))
            msg.attach(img)

        with smtplib.SMTP(smtp_server_ip, int(smtp_port), timeout=15) as smtp_server:
            smtp_server.sendmail(sender_email, recipient_email + [ccadd_email], msg.as_string())

        # Delete the graph image after email is sent
        os.remove(graph_filename)
        logger.info(f"Graph image {graph_filename} has been deleted after sending email.")

    except Exception as e:
        logger.error(f"Error sending email with attachment: {e}")
        raise

def fetch_data_for_date(es, index_name, date):
    """Fetch info from Elasticsearch for a given date."""
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "context.url": "http://myglapi.net/api/v1/campaigns/new-users/new-ga-2024"
                        }
                    }
                ]
            }
        },
        "aggs": {
            "context_status": {
                "terms": {
                    "field": "context.status",
                    "size": 10  # Adjust size based on the number of status types you expect
                }
            },
            "user_msisdn_count": {
                "cardinality": {
                    "field": "context.header_identification.keyword"
                }
            },
            "total_hits": {
                "scripted_metric": {
                    "init_script": "state.count = 0",
                    "map_script": "state.count += 1",
                    "combine_script": "return state.count",
                    "reduce_script": "return states.sum()"
                }
            }
        }
    }

    logger.debug(f"Executing query for date {date}: {query}")

    try:
        response = es.search(index=index_name, body=query, timeout="30s")
        logger.debug(f"Elasticsearch response: {response}")

        if 'aggregations' not in response:
            raise ValueError(f"No aggregations found in the Elasticsearch for {date}.")

        # Extract and return information
        aggregations = response['aggregations']
        context_status_buckets = aggregations.get('context_status', {}).get('buckets', [])
        user_msisdn_count = aggregations.get('user_msisdn_count', {}).get('value', 0)
        total_hits = aggregations.get('total_hits', {}).get('value', 0)

        # Create result with status codes broken out
        result = {
            'Date': date,
            'Total Count': total_hits,
            'Unique Users': user_msisdn_count
        }

        for bucket in context_status_buckets:
            status_code = bucket['key']
            doc_count = bucket['doc_count']
            result[f'Status_{status_code}'] = doc_count

        return result

    except Exception as e:
        logger.error(f"Error fetching data for {date}: {e}")
        raise

def create_bar_and_pie_graph(data_for_graph, graph_filename, status_counts, total_requests, unique_users):
    """Make a combined bar chart and two pie charts."""
    df = pd.DataFrame(data_for_graph)

    fig, axs = plt.subplots(1, 3, figsize=(21, 6))  # Create 1x3 subplot

    # Create a bar graph on the left side
    axs[0].bar(df['Date'], df['Total Count'], color='blue', width=0.5)
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Total Count')
    axs[0].set_title('Total Count of Requests Over Time')
    axs[0].grid(True, which='both', axis='y', linestyle='--', linewidth=0.7)
    axs[0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels

    # Create the first pie chart in the center
    axs[1].pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', startangle=140)
    axs[1].set_title('Distribution of Request Status')

    # Create the second pie chart on the right
    axs[2].pie([total_requests, unique_users], labels=['Total Requests', 'Unique Users'], autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff'])
    axs[2].set_title('Total Requests vs Unique Users')

    # Adjust layout
    plt.tight_layout()

    # Save graph to a file
    plt.savefig(graph_filename)
    plt.close()

def truncate_csv_if_needed(csv_file_path):
    """Cut down the CSV file to the last 15 days if over 5 MB."""
    max_size_mb = 5
    file_size_mb = os.path.getsize(csv_file_path) / (1024 * 1024)

    if file_size_mb > max_size_mb:
        df = pd.read_csv(csv_file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        last_15_days = df[df['Date'] >= (df['Date'].max() - pd.Timedelta(days=15))]
        last_15_days.to_csv(csv_file_path, index=False)
        logger.info(f"CSV file cut to last 15 days. New size: {os.path.getsize(csv_file_path) / (1024 * 1024):.2f} MB")

def main():
    parser = argparse.ArgumentParser(description="Get data from Elasticsearch, produce a report, and email it.")
    parser.add_argument('--forDaysBefore', type=int, default=7, help="Number of days before today to fetch data for.")
    args = parser.parse_args()

    try:
        es = create_es_client()

        days_before = args.forDaysBefore

        # Get the local timezone
        local_tz_name = config('LOCAL_TIMEZONE', default='UTC')
        local_tz = pytz.timezone(local_tz_name)

        # Get current local time (timezone-aware)
        local_now = datetime.datetime.now(local_tz)

        # Convert local time to UTC
        utc_now = local_now.astimezone(pytz.utc)

        end_date = utc_now - timedelta(days=1)
        start_date = end_date - timedelta(days_before - 1)

        all_data = []
        status_counts = {}
        total_requests = 0
        unique_users = 0

        # Iterate over the last few days
        for i in range(days_before):
            date_dt = start_date + timedelta(days=i)
            date = date_dt.strftime('%Y.%m.%d')
            index_name = f"api-app-{date}"
            data = fetch_data_for_date(es, index_name, date)

            # Sum status codes for the pie chart
            for key in data.keys():
                if key.startswith("Status_"):
                    status_code = key.split("_")[1]
                    status_counts[status_code] = status_counts.get(status_code, 0) + data[key]

            total_requests += data.get('Total Count', 0)
            unique_users += data.get('Unique Users', 0)

            all_data.append(data)

        # Convert the data to a DataFrame and save to CSV
        df = pd.DataFrame(all_data)
        csv_filename = "mygl_api_report.csv"
        if not os.path.exists(csv_filename):
            df.to_csv(csv_filename, index=False)
        else:
            df.to_csv(csv_filename, mode='a', header=False, index=False)

        truncate_csv_if_needed(csv_filename)

        # Create the graph and email it
        graph_filename = "mygl_api_report_graph.png"
        create_bar_and_pie_graph(all_data, graph_filename, status_counts, total_requests, unique_users)
        send_email_with_attachment(csv_filename, graph_filename)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()