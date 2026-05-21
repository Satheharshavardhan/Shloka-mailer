import json
import re

def clean_text(text):
    # Replaces multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    # Cleans up weird characters commonly misidentified by OCR in Sanskrit texts
    text = text.replace('`', '').replace('\\', '।')
    return text.strip()

def process():
    print("Loading chunks...")
    # Read the raw parsed PDF chunks
    with open('book_chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    # Filter out preliminary pages before the actual book content starts (page 15)
    pages = [c for c in chunks if c["page"] >= 15]
    
    # Combine all pages into one continuous string
    text = " ".join([c["content"] for c in pages])
    text = clean_text(text)
    
    # Improved parsing logic
    # Look for chapters
    # A chapter usually starts with "अथ ... अध्यायः" or ends with "इति ... अध्यायः"
    # But many sections start with "अथ ... स्वरूपम्" or "अथ ... माह"
    
    # We will split text by Shloka numbers.
    # Pattern to match end of a shloka or translation:
    # Captures the text before the number, and the number itself.
    # This pattern attempts to find the end of a shloka or translation.
    # It captures the text block and the trailing shloka number wrapped in Danda marks (। or ।।).
    pattern = re.compile(r'(.*?)(?:।।|। ।|।\s*।)([\u0966-\u096F\d]+(?:-[\u0966-\u096F\d]+)?)(?:।।|।\s*।|।|\)|\s*\\+)')
    
    matches = pattern.findall(text)
    
    shlokas = []
    
    current_chapter = "सृष्ट्यारम्भ"
    current_sanskrit = ""
    current_hindi = ""
    current_commentary = ""
    last_num = None
    
    # Helper function to convert Hindi numbers (e.g. १, २) into Arabic numbers (1, 2)
    def clean_num(n_str):
        return n_str.replace('१', '1').replace('२', '2').replace('३', '3').replace('४', '4').replace('५', '5').replace('६', '6').replace('७', '7').replace('८', '8').replace('९', '9').replace('०', '0')
    
    for match in matches:
        raw_content = match[0].strip()
        num_str = clean_num(match[1].strip())
        
        # Look for chapter headers in the text (e.g., अथ ... अध्यायः, अथ ... स्वरूपम्)
        chapter_match = re.search(r'अथ\s+([^\s।]+(?:ध्यायः|स्वरूपम्|माह|कथनम्|प्रकरणम्|विचारः))', raw_content)
        if chapter_match:
            current_chapter = chapter_match.group(1).replace('माह', '').replace('स्वरूपम्', ' स्वरूप')
        else:
            iti_match = re.search(r'इति पाराशरहोरायां.*?([^\s।]+ध्याय[^\s।]*?)\s*।', raw_content)
            if iti_match:
                current_chapter = iti_match.group(1)
        
        # Remove chapter declarations from the actual text to be shown
        content = re.sub(r'अथ\s+[^\s।]+(?:ध्यायः|स्वरूपम्|माह|कथनम्|प्रकरणम्|विचारः)[-\s।]*', '', raw_content)
        content = re.sub(r'इति पाराशरहोरायां.*?ध्याय[^\s।]*?\s*।+', '', content)
        content = re.sub(r'^(.*?उवाच[-\s]*)', '', content).strip()
        
        # Detect Commentary (often starts with उदाहरण or विमर्श)
        # Detect Commentary sections which usually start with 'उदाहरण-' (Example) or 'विमर्श-'
        comm_match = re.search(r'(उदाहरण[-:]|विमर्श[-:])(.*)', content)
        if comm_match:
            current_commentary += " " + comm_match.group(0).strip()
            content = content[:comm_match.start()].strip()
            
        if num_str != last_num:
            # We found a new number, so the PREVIOUS number's Sanskrit/Hindi is completely finished.
            # Append it to the shlokas array.
            if current_sanskrit:
                shlokas.append({
                    "chapter": current_chapter,
                    "shloka": last_num,
                    "sanskrit": current_sanskrit.strip(),
                    "hindi": current_hindi.strip(),
                    "commentary": current_commentary.strip()
                })
            # Start accumulating for the new Shloka
            current_sanskrit = content
            current_hindi = ""
            current_commentary = ""
            last_num = num_str
        else:
            # The number is the same as the last seen, meaning this is likely the Hindi translation.
            current_hindi = content
            
    # Add the last one
    if current_sanskrit:
         shlokas.append({
             "chapter": current_chapter,
             "shloka": last_num,
             "sanskrit": current_sanskrit.strip(),
             "hindi": current_hindi.strip(),
             "commentary": current_commentary.strip()
         })
         
    # Because the OCR on page 15-16 is very messy, we hardcode the first 6 shlokas perfectly here.
    perfect_shlokas = [
        {
            "chapter": "सृष्ट्यारम्भ",
            "shloka": "१",
            "sanskrit": "मैत्रेय उवाच-\nनमस्तस्मै भगवते बोधरूपाय सर्वदा।\nपरमानन्दकन्दाय गुरवेऽज्ञानध्वंसिने।।१।।",
            "hindi": "मैत्रेय जी ज्योतिषशास्त्र के सार पदार्थं को जानने के लिए पाराशर जी की स्तुति करते है। अज्ञान को नाश करने वाले, परम आनन्द को देने वाले, सर्वदा ज्ञान को देने वाले भगवन्‌ परमपूज्य आपको नमस्कार है।",
            "commentary": ""
        },
        {
            "chapter": "सृष्ट्यारम्भ",
            "shloka": "२",
            "sanskrit": "इति स्तुत्या सुसंहृष्टो मुनिस्तत्त्वविदाम्बरः।\nअथादिदेश सच्छास्त्रं सारं यज्ज्योतिषां शुभम्‌।।२।।",
            "hindi": "इस स्तुति से तत्त्व के जानने वालों में श्रेष्ठ मुनि प्रसन्न होकर ज्योतिष (ग्रहों) के तत्त्व शास्त्र का आदेश करने लगे।",
            "commentary": ""
        },
        {
            "chapter": "सृष्ट्यारम्भ",
            "shloka": "३",
            "sanskrit": "पराशर उवाच-\nशुक्लाम्बरधरं विष्णुं शुक्लाम्बरधरां गिरम्‌।\nप्रणम्य पाञ्चजन्यं च वीणां याभ्यां धृतं द्वयम्‌।।३।।",
            "hindi": "पराशर जी बोले- सफेद वस्त्र को धारण किये हुये, पाञ्चजन्य शंख को लिये हुये विष्णु को एवं सफेद वस्त्र को धारण किये हुये, वीणा को लिये हुये सरस्वती को प्रणाम कर।",
            "commentary": ""
        },
        {
            "chapter": "सृष्ट्यारम्भ",
            "shloka": "४",
            "sanskrit": "सूर्यं नत्वा ग्रहपतिं जगदुत्पत्तिकारणम्‌।\nवक्ष्यामि वेदनयनं यथा ब्रह्ममुखाच्छ्रुतम्‌।।४।।",
            "hindi": "संसार के उत्पत्ति के कारण, ग्रहों के स्वामी सूर्य को नमस्कार करके, जैसा मैने ब्रह्मा के मुख से सुना है, वैसा ही वेद के नेत्र (ज्योतिष-शास्त्र) को कहूँगा।",
            "commentary": ""
        },
        {
            "chapter": "सृष्ट्यारम्भ",
            "shloka": "५",
            "sanskrit": "शान्ताय गुरुभक्ताय ऋजवेऽचितस्वामिने।\nआस्तिकाय प्रदातव्यं ततः श्रेयो ह्यवाप्यति।।५।।",
            "hindi": "इस शास्त्र को शान्तस्वभाव, गुरुभक्त, सीधे, स्वामीभक्त और आस्तिक को देना चाहिए। इससे कल्याण की प्राप्ति होती है।",
            "commentary": ""
        },
        {
            "chapter": "सृष्ट्यारम्भ",
            "shloka": "६",
            "sanskrit": "न देयं परशिष्याय नास्तिकाय शठाय च।\nदत्ते प्रतिदिनं दुःखं जायते नात्र संशयः।।६।।",
            "hindi": "दूसरे के शिष्य को, नास्तिक और शठ को नहीं देना चाहिए। ऐसा करने से प्रतिदिन दुःख होता है, इसमें संशय नहीं है।",
            "commentary": ""
        }
    ]
    
    final_shlokas = perfect_shlokas.copy()
    
    # Filter out duplicates (the first 6) and extremely messy OCR artifacts
    for s in shlokas:
        # Ignore the first 6 we manually added, and some weird OCR artifacts
        if s["shloka"] not in ["1", "2", "3", "4", "5", "6", "1-2"] and len(s["shloka"]) < 4:
            # A valid shloka must have at least some length of text (e.g. >10 chars)
            if len(s["sanskrit"]) > 10:
                final_shlokas.append(s)

    # Save the highly accurate data to JSON
    with open('structured_shlokas.json', 'w', encoding='utf-8') as f:
        json.dump(final_shlokas, f, ensure_ascii=False, indent=2)
        
    print(f"Extraction complete! Saved {len(final_shlokas)} highly accurate shlokas.")

if __name__ == "__main__":
    process()
