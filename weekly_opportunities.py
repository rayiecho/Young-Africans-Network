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


INTERNSHIPS = [
    {'title':'UN Youth Volunteer Programme 2025','company':'United Nations','location':'Various African offices','type':'Internship','deadline':'Rolling','link':'https://www.unv.org','description':'6-12 month volunteer internship with UN agencies across Africa','category':'internship','duration':'6-12 months','stipend':'Monthly allowance provided'},
    {'title':'African Development Bank Internship','company':'African Development Bank','location':'Abidjan, Ivory Coast','type':'Internship','deadline':'March & September annually','link':'https://www.afdb.org/en/careers/internships','description':'6-month internship in finance, economics, or development','category':'internship','duration':'6 months','stipend':'Paid'},
    {'title':'World Health Organization Africa Internship','company':'WHO Africa','location':'Brazzaville, Congo','type':'Internship','deadline':'Rolling','link':'https://www.who.int/careers/internships','description':'Health policy and program internship in Africa','category':'internship','duration':'6 months','stipend':'Unpaid with allowance'},
    {'title':'Google Africa Developer Internship','company':'Google','location':'Remote / Nairobi / Lagos','type':'Internship','deadline':'Rolling','link':'https://careers.google.com','description':'Software engineering internship for African developers','category':'internship','duration':'3-6 months','stipend':'Paid'},
    {'title':'Microsoft Africa Research Institute Internship','company':'Microsoft','location':'Nairobi, Kenya','type':'Internship','deadline':'Rolling','link':'https://www.microsoft.com/en-us/research/lab/microsoft-research-africa','description':'AI and technology research internship','category':'internship','duration':'3-6 months','stipend':'Paid'},
    {'title':'UNICEF Africa Internship Programme','company':'UNICEF','location':'Various African countries','type':'Internship','deadline':'Rolling','link':'https://www.unicef.org/careers/internships','description':'Work on child rights and development programs','category':'internship','duration':'6 months','stipend':'Stipend provided'},
    {'title':'African Union Commission Internship','company':'African Union','location':'Addis Ababa, Ethiopia','type':'Internship','deadline':'January & July annually','link':'https://au.int/en/internship','description':'Policy and governance internship at AU headquarters','category':'internship','duration':'6 months','stipend':'Paid'},
    {'title':'GIZ Africa Internship','company':'GIZ Germany','location':'Various African countries','type':'Internship','deadline':'Rolling','link':'https://www.giz.de/en/html/jobs.html','description':'Development cooperation internship across Africa','category':'internship','duration':'3-6 months','stipend':'Paid'},
    {'title':'Safaricom Internship Programme','company':'Safaricom','location':'Nairobi, Kenya','type':'Internship','deadline':'Rolling','link':'https://www.safaricom.co.ke/careers','description':'Tech and business internship at Africa leading telco','category':'internship','duration':'3 months','stipend':'Paid'},
    {'title':'MTN Group Internship','company':'MTN Group','location':'Johannesburg / Various African countries','type':'Internship','deadline':'Rolling','link':'https://www.mtn.com/careers','description':'Telecommunications and digital services internship','category':'internship','duration':'3-6 months','stipend':'Paid'},
]

FELLOWSHIPS = [
    {'title':'Obama Foundation Leaders Africa Program','company':'Obama Foundation','location':'Various African cities','type':'Fellowship','deadline':'February annually','link':'https://www.obama.org/programs/leaders/africa','description':'Leadership fellowship for African change-makers under 40','category':'fellowship','duration':'1 year','stipend':'Fully funded'},
    {'title':'Mandela Washington Fellowship','company':'US Department of State','location':'USA + home country','type':'Fellowship','deadline':'November annually','link':'https://yali.state.gov/mwf','description':'6-week leadership institute in USA for African youth','category':'fellowship','duration':'6 weeks','stipend':'Fully funded'},
    {'title':'Acumen East Africa Fellowship','company':'Acumen','location':'East Africa','type':'Fellowship','deadline':'February annually','link':'https://acumen.org/fellowships','description':'Social enterprise leadership fellowship','category':'fellowship','duration':'1 year','stipend':'Stipend provided'},
    {'title':'African Leadership Academy Fellowship','company':'African Leadership Academy','location':'Johannesburg, South Africa','type':'Fellowship','deadline':'October annually','link':'https://www.africanleadershipacademy.org','description':'Leadership development for young African leaders','category':'fellowship','duration':'2 years','stipend':'Scholarship + stipend'},
    {'title':'Aspen New Voices Fellowship','company':'Aspen Institute','location':'Various','type':'Fellowship','deadline':'Rolling','link':'https://www.aspeninstitute.org','description':'Fellowship for African development thinkers and practitioners','category':'fellowship','duration':'1 year','stipend':'Fully funded'},
    {'title':'Atlantic Fellows for Social and Economic Equity','company':'Atlantic Institute','location':'London + Africa','type':'Fellowship','deadline':'January annually','link':'https://www.atlanticfellows.org','description':'Fellowship addressing inequality in Africa','category':'fellowship','duration':'1 year','stipend':'Fully funded'},
    {'title':'Schwarzman Scholars Program','company':'Schwarzman College','location':'Beijing, China','type':'Fellowship','deadline':'September annually','link':'https://www.schwarzmanscholars.org','description':'Masters degree fellowship at Tsinghua University','category':'fellowship','duration':'1 year','stipend':'Fully funded'},
    {'title':'African Development Bank Young Professionals','company':'African Development Bank','location':'Abidjan, Ivory Coast','type':'Fellowship','deadline':'January annually','link':'https://www.afdb.org/en/careers/young-professionals-program','description':'3-year professional fellowship at AfDB','category':'fellowship','duration':'3 years','stipend':'Full salary'},
    {'title':'TED Fellows Program','company':'TED','location':'Remote + TED Conference','type':'Fellowship','deadline':'May annually','link':'https://fellowships.ted.com','description':'Fellowship for innovative African thinkers and doers','category':'fellowship','duration':'2 years','stipend':'Travel + support'},
    {'title':'Hubert H. Humphrey Fellowship','company':'US Department of State','location':'USA','type':'Fellowship','deadline':'October annually','link':'https://www.humphreyfellowship.org','description':'10-month professional development fellowship in USA','category':'fellowship','duration':'10 months','stipend':'Fully funded'},
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
    print("\n🎓 Posting internships...")
    for i in INTERNSHIPS:
        doc_id = f"weekly-{week}-intern-{i['title'][:25].replace(' ','-').lower()}"
        db.collection("careerJobs").document(doc_id).set({**i,"postedAt":now,"postedById":"yan-bot","weekRef":week,"verified":True,"status":"active"})
        posted += 1
        print(f"  ✅ {i['title'][:50]}")
    print("\n🌟 Posting fellowships...")
    for f in FELLOWSHIPS:
        doc_id = f"weekly-{week}-fellow-{f['title'][:25].replace(' ','-').lower()}"
        db.collection("careerJobs").document(doc_id).set({**f,"postedAt":now,"postedById":"yan-bot","weekRef":week,"verified":True,"status":"active"})
        posted += 1
        print(f"  ✅ {f['title'][:50]}")
    print("\n💰 Posting grants...")
    for g in GRANTS:
        doc_id = f"weekly-{week}-grant-{g['title'][:30].replace(' ','-').lower()}"
        db.collection("scholarships").document(doc_id).set({**g,"postedAt":now,"postedBy":"YAN Opportunities Bot","weekRef":week,"verified":True,"status":"active","funding":g["amount"]})
        posted += 1
        print(f"  ✅ {g['title'][:50]}")
    try:
        db.collection("notifications").add({"title":"🌍 New Opportunities This Week!","message":"10 scholarships, 10 jobs, 10 internships, 10 fellowships and 10 grants posted this week. Check YAN now!","type":"opportunity","postedBy":"YAN Opportunities Bot","createdAt":now,"readBy":[]})
        print(f"\n🔔 Notification sent to all members!")
    except Exception as e:
        print(f"⚠️  Notification failed: {e}")
    print(f"\n🎉 Done! {posted} opportunities posted for week {week}")

post_opportunities()
