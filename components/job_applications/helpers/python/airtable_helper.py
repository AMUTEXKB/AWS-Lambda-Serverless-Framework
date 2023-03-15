import os

from dotenv import load_dotenv
from pyairtable import Table, Api
from pyairtable.formulas import match
from pyairtable.utils import attachment

"""
User Code, Job Link, All Opportunities fields should not be renamed, because formula method works only with field names, not ids
"""
load_dotenv()  # todo remove
APPLICANTS_BASE_ID = 'apptRvTE9Dby0WMYy'
APPLICANTS_TABLE_NAME = 'Applicants'
TRACKER_TABLE_NAME = 'Tracker'
OPPORTUNITIES_TABLE_NAME = 'All opportunities'
api_key = os.environ["AIRTABLE_API_KEY"]
DEFAULT_STATUS = 'Application received'
# presigned
file_url = ''
api = Api(api_key)

OPPORTUNITIES_FIELD_NAME = 'All Opportunities'

applicants_field_ids = {
    'First Name': 'fldSugaFEG3iAHnAE',
    'Last Name': 'fldozuHlT6xP5wwe8',
    'Full Name': 'fldUMnIwmatXcin4G',
    'User Code': 'fld1ApQtASUnx7dbG',
    'University': 'fldPkdOGO2x5EFTc2',
    'Email': 'fldS5xzBCfUJvWS1a',
    'LinkedIn': 'fldWbdQVKXgKwQOPS',
    OPPORTUNITIES_FIELD_NAME: 'fldGKK9IOj101CBV2',
    'Candidate status': 'fldP4QpqlOeNJdWoD',
}

tracker_field_ids = {
    'Applicants': 'fldovmcphPK9H6iCX',
    OPPORTUNITIES_FIELD_NAME: 'fldrIwsNOLshk1V37',
    'First Name': 'fldXlhoDu8E06dra1',
    'Cover Letter': 'fld2sOc5zSBm5TToU',
    'CV': 'fld1kOfD0RUNwqrVR',
    'Candidate Status': 'fldONLtQ7DZ5UxqqJ'

}

opportunities_field_ids = {
    'Job Link': 'fld14jzEnje8TJUOe'
}


class ApplicantsTable:
    def __init__(self):
        self.table_records = Table(api_key, APPLICANTS_BASE_ID, APPLICANTS_TABLE_NAME)
        self.all_records = self.table_records.all()

    def get_applicant(self, user_code: str):
        formula = match({'User Code': user_code})
        return self.table_records.first(formula=formula)

    def add(self, body, user_context, opportunity_record_id=None) -> str:
        """
        creates an applicant if it's new else updates applied jobs field
        """
        record_id = None
        user_code = user_context['id']
        applicant = self.get_applicant(user_code)
        if applicant:
            opportunities = applicant['fields'][OPPORTUNITIES_FIELD_NAME]
            if opportunity_record_id not in opportunities:
                opportunities.append(opportunity_record_id)
                record_id = self.table_records.update(applicant['id'],
                                                      {applicants_field_ids[OPPORTUNITIES_FIELD_NAME]: opportunities})[
                    'id']

        else:
            record_id = self.table_records.create({
                applicants_field_ids['First Name']: body['first_name'],
                applicants_field_ids['Last Name']: body['last_name'],
                applicants_field_ids['Full Name']: body['first_name'] + ' ' + body['last_name'],
                applicants_field_ids['University']: body['university'],
                applicants_field_ids['Email']: body['email'],
                applicants_field_ids['LinkedIn']: body['linkedin'],
                applicants_field_ids['User Code']: user_code,
                applicants_field_ids[OPPORTUNITIES_FIELD_NAME]: [opportunity_record_id]
            }
            )['id']
        return record_id


class TrackerTable:
    def __init__(self):
        self.table_records = Table(api_key, APPLICANTS_BASE_ID, TRACKER_TABLE_NAME)

    def add(self, body, applicant_record_id: str, opportunity_record_id: str):
        record_id = self.table_records.create({
            tracker_field_ids['Applicants']: [applicant_record_id],
            tracker_field_ids[OPPORTUNITIES_FIELD_NAME]: [opportunity_record_id],
            tracker_field_ids['Candidate Status']: DEFAULT_STATUS,
            tracker_field_ids['CV']: [attachment(file_url, filename='CV')],
            tracker_field_ids['Cover Letter']: body['cover_letter'],
        })
        return record_id


class OpportunitiesTable:
    def __init__(self):
        self.table_records = Table(api_key, APPLICANTS_BASE_ID, OPPORTUNITIES_TABLE_NAME)

    def add(self, body):
        pass


# todo remove mocks
body = {
    'first_name': 'Violetta',
    'last_name': 'Gaidak',
    'university': 'Sloan',
    'email': 'violetta@test.com',
    'linkedin': 'linkedin',
    'job_link': 'https://app.pioneers-education.com/jobs/20',
    'cover_letter': 'Cover Letter test'
}

user_context = {
    'id': 'Violetta test code'
}

applicants_table = ApplicantsTable()
tracker_table = TrackerTable()
opportunities_table = OpportunitiesTable()


def update_applicants_base():
    # get field ids
    # records = applicants_table.table_records.all()
    # record_1 = api.get(APPLICANTS_BASE_ID, APPLICANTS_TABLE_NAME, 'recL2Qx32XG7BjgCv', return_fields_by_field_id=True)
    applicant_tracker_record_id = None
    # get job record id
    formula = match({'Job Link': body['job_link']})
    opportunity_record_id = opportunities_table.table_records.first(formula=formula)['id']
    # add a new applicant or update an existing one
    applicant_record_id = applicants_table.add(body=body, user_context=user_context,
                                               opportunity_record_id=opportunity_record_id)
    # add an application to the tracker
    if applicant_record_id:
        applicant_tracker_record_id = tracker_table.add(body=body, opportunity_record_id=opportunity_record_id,
                                                        applicant_record_id=applicant_record_id)
    return applicant_tracker_record_id

# update_applicants_base()
