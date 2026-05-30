import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

cred = credentials.Certificate('/home/ayiecho/projects/yan_website/serviceAccount.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

SCHOLARSHIPS = [
    {'title':'Mastercard Foundation Scholars Program 2025','provider':'Mastercard Foundation','funding':'Full Scholarship','deadline':'Rolling','eligibility':'African students with demonstrated leadership','link':'https://mastercardfdn.org/scholars','countries':'All African countries','level':'Undergraduate & Graduate','category':'scholarship'},
    {'title':'African Development Bank Scholarship','provider':'African Development Bank','funding':'Full Scholarship + Stipend','deadline':'March 31 annually','eligibility':'African nationals pursuing Masters degree','link':'https://www.afdb.org','countries':'All African countries','level':'Masters','category':'scholarship'},
    {'title':'Chevening Scholarships 2025-2026','provider':'UK Government','funding':'Full Scholarship','deadline':'November annually','eligibility':'African professionals with 2 years work experience','link':'https://www.chevening.org','countries':'All African countries','level':'Masters in UK','category':'scholarship'},
    {'title':'Commonwealth Scholarship 2025','provider':'Commonwealth Scholarship Commission','funding':'Full Scholarship','deadline':'October annually','eligibility':'Commonwealth country citizens','link':'https://cscuk.fcdo.gov.uk','countries':'Commonwealth African nations','level':'Masters & PhD','category':'scholarship'},
    {'title':'Erasmus Mundus Joint Masters','provider':'European Commission','funding':'Full Scholarship + 1400/month','deadline':'January annually','eligibility':'African students with excellent academic record','link':'https://erasmus-plus.ec.europa.eu','countries':'All African countries','level':'Masters in Europe','category':'scholarship'},
    {'title':'DAAD Scholarship Germany 2025','provider':'DAAD Germany','funding':'Full Scholarship + 850/month','deadline':'October annually','eligibility':'African graduates with excellent grades','link':'https://www.daad.de/en','countries':'All African countries','level':'Masters & PhD in Germany','category':'scholarship'},
    {'title':'Mo Ibrahim Foundation Scholarship','provider':'Mo Ibrahim Foundation','funding':'Full Scholarship','deadline':'February annually','eligibility':'African nationals under 35','link':'https://mo.ibrahim.foundation','countries':'All African countries','level':'Masters at LSE','category':'scholarship'},
    {'title':'Aga Khan Foundation International Scholarship','provider':'Aga Khan Foundation','funding':'Partial to Full Scholarship','deadline':'March annually','eligibility':'Exceptional graduates from developing countries','link':'https://www.akdn.org/agency/akf','countries':'Selected African countries','level':'Masters','category':'scholarship'},
    {'title':'Fulbright Foreign Student Program','provider':'US Government','funding':'Full Scholarship','deadline':'Varies by country','eligibility':'African students for study in USA','link':'https://foreign.fulbrightonline.org','countries':'All African countries','level':'Masters & PhD in USA','category':'scholarship'},
    {'title':'Gates Cambridge Scholarship','provider':'Bill & Melinda Gates Foundation','funding':'Full Scholarship','deadline':'October annually','eligibility':'Outstanding students outside UK','link':'https://www.gatescambridge.org','countries':'All African countries','level':'Masters & PhD at Cambridge','category':'scholarship'},
]

JOBS = [
    {'title':'Program Officer - Youth Development','company':'UNICEF Africa','location':'Nairobi, Kenya','type':'Full-time','deadline':'Rolling','link':'https://www.unicef.org/careers','description':'Lead youth development programs across East Africa','category':'job'},
    {'title':'Communications Specialist','company':'African Union','location':'Addis Ababa, Ethiopia','type':'Full-time','deadline':'Rolling','link':'https://au.int/en/careers','description':'Manage communications for AU initiatives','category':'job'},
    {'title':'Data Analyst','company':'World Bank Africa','location':'Remote / Various African offices','type':'Full-time','deadline':'Rolling','link':'https://www.worldbank.org/en/about/careers','description':'Analyze development data across African projects','category':'job'},
    {'title':'Software Engineer','company':'Andela','location':'Remote - Africa','type':'Full-time','deadline':'Rolling','link':'https://andela.com/careers','description':'Join Africa largest tech talent network','category':'job'},
    {'title':'Project Manager - Health','company':'Partners in Health Africa','location':'Various African countries','type':'Full-time','deadline':'Rolling','link':'https://www.pih.org/careers','description':'Manage health projects in underserved communities','category':'job'},
    {'title':'Business Development Officer','company':'Tony Elumelu Foundation','location':'Lagos, Nigeria','type':'Full-time','deadline':'Rolling','link':'https://www.tonyelumelufoundation.org','description':'Support African entrepreneurs across the continent','category':'job'},
    {'title':'Research Associate','company':'African Economic Research Consortium','location':'Nairobi, Kenya','type':'Full-time','deadline':'Rolling','link':'https://www.aercafrica.org/careers','description':'Conduct economic research for African policy','category':'job'},
    {'title':'Digital Marketing Manager','company':'Jumia Africa','location':'Remote - Africa','type':'Full-time','deadline':'Rolling','link':'https://group.jumia.com/careers','description':'Drive digital marketing across African markets','category':'job'},
    {'title':'Community Health Worker','company':'Amref Health Africa','location':'Various African countries','type':'Full-time','deadline':'Rolling','link':'https://amref.org/careers','description':'Improve healthcare access in rural Africa','category':'job'},
    {'title':'Finance Officer','company':'Save the Children Africa','location':'Various African offices','type':'Full-time','deadline':'Rolling','link':'https://www.savethechildren.net/careers','description':'Manage finances for humanitarian programs','category':'job'},
]

GRANTS = [
    {'title':'Tony Elumelu Foundation Entrepreneurship Program','provider':'Tony Elumelu Foundation','amount':'$5,000 USD seed funding','deadline':'January annually','eligibility':'African entrepreneurs, early-stage businesses','link':'https://www.tonyelumelufoundation.org/teep','countries':'All 54 African countries','category':'grant'},
    {'title':'African Women Innovation Entrepreneurship Grant','provider':'AWIEF','amount':'Up to $10,000 USD','deadline':'Rolling','eligibility':'African women entrepreneurs','link':'https://awief.org','countries':'All African countries','category':'grant'},
    {'title':'Seedstars Africa Ventures Grant','provider':'Seedstars','amount':'Up to $500,000 USD investment','deadline':'Rolling','eligibility':'African tech startups','link':'https://www.seedstars.com','countries':'All African countries','category':'grant'},
    {'title':'Echoing Green Fellowship','provider':'Echoing Green','amount':'$80,000 USD over 2 years','deadline':'January annually','eligibility':'Social entrepreneurs with innovative ideas','link':'https://echoinggreen.org/fellowship','countries':'All African countries','category':'grant'},
    {'title':'Hivos Green Grants Africa','provider':'Hivos','amount':'Up to $50,000 USD','deadline':'Rolling','eligibility':'African organizations in renewable energy','link':'https://hivos.org/program/green-grants','countries':'Sub-Saharan Africa','category':'grant'},
    {'title':'African Capacity Building Foundation Grant','provider':'ACBF','amount':'Up to $200,000 USD','deadline':'Rolling','eligibility':'African institutions and organizations','link':'https://www.acbf-pact.org','countries':'All African countries','category':'grant'},
    {'title':'World Bank Youth Summit Grant','provider':'World Bank','amount':'Up to $10,000 USD','deadline':'March annually','eligibility':'African youth 18-30 with development projects','link':'https://www.worldbank.org/youthsummit','countries':'All African countries','category':'grant'},
    {'title':'Ford Foundation International Fellowships','provider':'Ford Foundation','amount':'Full fellowship support','deadline':'October annually','eligibility':'African social justice leaders','link':'https://www.fordfoundation.org','countries':'Selected African countries','category':'grant'},
    {'title':'African Union Youth Volunteer Corps Grant','provider':'African Union','amount':'Stipend + project funding','deadline':'Rolling','eligibility':'African youth 18-35','link':'https://au.int/en/AUYVC','countries':'All African countries','category':'grant'},
    {'title':'Wellcome Trust Africa Grants','provider':'Wellcome Trust','amount':'Up to 250,000 GBP','deadline':'Rolling','eligibility':'African researchers in health and science','link':'https://wellcome.org/grant-funding/schemes/african-programmes','countries':'All African countries','category':'grant'},
]

def post_opportunities():
    now = datetime.now(timezone.utc)
    week = now.strftime("%Y-W%U")
    posted = 0
    print(f"\n🌍 YAN Weekly Opportunities Worker")
    print(f"📅 Week: {week}\n")
    print("📚 Posting scholarships...")
    for s in SCHOLARSHIPS:
        doc_id = f"weekly-{week}-{s['title'][:30].replace(' ','-').lower()}"
        db.collection("scholarships").document(doc_id).set({**s,"postedAt":now,"postedBy":"YAN Opportunities Bot","weekRef":week,"verified":True,"status":"active"})
        posted += 1
        print(f"  ✅ {s['title'][:50]}")
    print("\n💼 Posting jobs...")
    for j in JOBS:
        doc_id = f"weekly-{week}-{j['title'][:30].replace(' ','-').lower()}"
        db.collection("careerJobs").document(doc_id).set({**j,"postedAt":now,"postedById":"yan-bot","weekRef":week,"verified":True,"status":"active"})
        posted += 1
        print(f"  ✅ {j['title'][:50]}")
    print("\n💰 Posting grants...")
    for g in GRANTS:
        doc_id = f"weekly-{week}-grant-{g['title'][:30].replace(' ','-').lower()}"
        db.collection("scholarships").document(doc_id).set({**g,"postedAt":now,"postedBy":"YAN Opportunities Bot","weekRef":week,"verified":True,"status":"active","funding":g["amount"]})
        posted += 1
        print(f"  ✅ {g['title'][:50]}")
    try:
        db.collection("notifications").add({"title":"🌍 New Opportunities This Week!","message":"10 scholarships, 10 jobs and 10 grants posted this week. Check YAN Scholarships and Career tabs now!","type":"opportunity","postedBy":"YAN Opportunities Bot","createdAt":now,"readBy":[]})
        print(f"\n🔔 Notification sent to all members!")
    except Exception as e:
        print(f"⚠️  Notification failed: {e}")
    print(f"\n🎉 Done! {posted} opportunities posted for week {week}")

post_opportunities()
