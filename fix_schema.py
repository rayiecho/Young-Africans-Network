import json, re

with open('index.html', 'r') as f:
    content = f.read()

new_schema = '''{
  "@context": "https://schema.org",
  "@type": "NGO",
  "name": "Young Africans Network",
  "alternateName": "YAN",
  "description": "Young Africans Network (YAN) is a pan-African, youth-led volunteer organization founded in Kenya in April 2026, empowering African youth through education, leadership, mentorship and access to global opportunities.",
  "url": "https://youngafricansnetwork.org",
  "logo": "https://youngafricansnetwork.org/images/logo.jpeg",
  "image": "https://youngafricansnetwork.org/images/logo.jpeg",
  "slogan": "Building the Future, Together",
  "foundingDate": "2026-04",
  "foundingLocation": {"@type": "Place","name": "Kenya, Africa"},
  "areaServed": "Africa",
  "email": "info@youngafricansnetwork.org",
  "telephone": "",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "",
    "email": "info@youngafricansnetwork.org",
    "contactType": "General Inquiry"
  },
  "founder": [
    {
      "@type": "Person",
      "name": "Emmanuel Ikumilu Mwori",
      "jobTitle": "Founder & Executive Director"
    },
    {
      "@type": "Person",
      "name": "Regan Odhiambo Ayiecho",
      "jobTitle": "Co-Founder & Tech Lead",
      "url": "https://rayiecho.github.io"
    }
  ],
  "sameAs": [
    "https://www.linkedin.com/company/115838329",
    "https://www.instagram.com/youngafricansnetwork",
    "https://www.facebook.com/profile.php?id=61589163254586",
    "https://x.com/YoungAfricanNet",
    "https://www.youtube.com/channel/UCo5ptDN88YdQ86RI2yu45ZA"
  ]
}'''

updated = re.sub(
    r'<script type="application/ld\+json">.*?</script>',
    f'<script type="application/ld+json">\n{new_schema}\n</script>',
    content, flags=re.DOTALL, count=1
)

with open('index.html', 'w') as f:
    f.write(updated)

print("✅ Schema updated on index.html")
