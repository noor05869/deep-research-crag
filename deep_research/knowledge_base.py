"""
deep_research/knowledge_base.py
-------------------------------
Internal company knowledge base documents for retrieval.
"""

from typing import List, Dict

INTERNAL_DOCUMENTS: List[Dict[str, str]] = [
    {
        "doc_id": "doc_museum_001",
        "title": "Museum Fossil Collection Procedures",
        "content": """Purpose and collection scope:
This guide explains how the Stonevale Natural History Museum receives, documents, stores, and lends fossil specimens. It covers preserved animal and plant remains, casts, and associated field notes. The collection supports research and education. The collections curator decides whether a proposed donation fits the museum's collecting scope.

Receiving a specimen:
Before accepting a donation, staff obtain the donor's name, a description of the specimen, ownership history, and any available collecting permits. Record the discovery location, geological formation, and estimated geological age when known. Do not invent missing provenance. Place newly received specimens in the intake area until the curator completes the acceptance review.

Cataloging and identification:
After acceptance, assign a unique accession number using the pattern SVM followed by the year and a sequential four digit number. Record the specimen name, material type, dimensions, condition, provenance, and storage location in the collection database. Photograph the specimen from at least three angles with a scale marker. Keep the accession label with the specimen without writing directly on its surface.

Handling and storage:
Support fragile specimens with both hands or move them on a padded tray. Never lift a fossil by a thin projection such as a tooth, rib, or leaf impression. Store small specimens in labeled archival boxes with suitable padding. Keep heavy specimens on lower shelves. Refer cracking, flaking, or suspected mineral decay to the conservator before cleaning or repair.

Research visits and loans:
Researchers must request an appointment at least ten business days before a collection visit. Include the research purpose and accession numbers of interest. External loans require curator approval and a signed loan agreement. The standard loan period is 60 calendar days. Borrowers must obtain written permission before sampling, scanning with treatments, or making any permanent alteration.

Return and incident records:
On return from a loan, compare each specimen with its departure photographs and condition report. Record new damage, missing labels, and packaging problems before returning the specimen to storage. Notify the collections curator immediately if a specimen is lost or damaged. Only the conservator authorizes stabilization or restoration treatments."""
    },
    {
        "doc_id": "doc_remote_002",
        "title": "Employee Remote Work Policy",
        "content": """Purpose and eligibility:
This policy explains how employees at Cedarbridge Design Studio request remote work, remain available, and protect company information. Permanent employees may apply after completing 60 calendar days of employment. Contractors and interns are outside the scope of this policy. Remote arrangements require written approval from the employee's manager.

Work schedule and availability:
Approved employees may work remotely up to three days per week. Tuesday and Thursday are office collaboration days. Core availability is 10 am to 3 pm in the employee's assigned office time zone, excluding an agreed lunch break. Employees must keep their work calendar current and notify their manager before changing a scheduled remote day.

Request and approval process:
Submit a remote work request through the employee portal at least five business days before the proposed start date. Include the requested days, work location, and a plan for attending team meetings. The manager reviews role requirements and team coverage, then records approval or a reason for denial in the portal. Approval remains valid for 90 days before review.

Equipment and expenses:
The company supplies one laptop, one headset, and access to approved collaboration software. Employees may claim up to 40 credits per month for home internet using an itemized receipt. Furniture, electricity, and personal mobile plans are not reimbursed. Equipment faults should be reported to the IT help desk, and company devices must be returned when employment ends.

Information security:
Employees must connect through the company VPN when accessing internal systems and use multifactor authentication on company accounts. Lock the screen when leaving the workstation. Store work files in approved company storage rather than personal cloud accounts. Report a lost device or suspected account compromise to IT immediately.

Performance and exceptions:
Managers evaluate completed work, quality, and agreed deadlines. Remote work does not change performance expectations or leave procedures. An employee seeking a temporary exception to office attendance must obtain written manager approval. Human Resources handles questions about eligibility; IT handles technical access issues."""
    }
]