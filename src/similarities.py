# This file is used for single view mogodb database topic modelling
# Daniel Dai
from gensim import corpora, models, similarities, matutils, utils
from stopwords import get_stopwords
from collections import defaultdict
from editdistance import *
import numpy as np
from six import iteritems

TestData = {
    "Dental_Pain": {
        "HISTORY_OF_PRESENT_ILLNESS": "This is a 27-year-old female who presents with a couple of days history of some dental pain. She has had increasing swelling and pain to the left lower mandible area today. Presents now for evaluation",
        "PAST_MEDICAL_HISTORY": "Remarkable for chronic back pain, neck pain from a previous cervical fusion, and degenerative disc disease. She has chronic pain in general and is followed by Dr. X",
        "REVIEW_OF_SYSTEMS": "Otherwise, unremarkable. Has not noted any fever or chills. However she, as mentioned, does note the dental discomfort with increasing swelling and pain. Otherwise, unremarkable except as noted",
        "CURRENT_MEDICATIONS": "Please see list",
        "ALLERGIES": "IODINE, FISH OIL, FLEXERIL, BETADINE",
        "PHYSICAL_EXAMINATION": "VITAL SIGNS: The patient was afebrile, has stable and normal vital signs. The patient is sitting quietly on the gurney and does not look to be in significant distress, but she is complaining of dental pain. HEENT: Unremarkable. I do not see any obvious facial swelling, but she is definitely tender all in the left mandible region. There is no neck adenopathy. Oral mucosa is moist and well hydrated. Dentition looks to be in reasonable condition. However, she definitely is tender to percussion on the left lower first premolar. I do not see any huge cavity or anything like that. No real significant gingival swelling and there is no drainage noted. None of the teeth are tender to percussion",
        "PROCEDURE": "Dental nerve block. Using 0.5% Marcaine with epinephrine, I performed a left inferior alveolar nerve block along with an apical nerve block, which achieves good anesthesia. I have then written a prescription for penicillin and Vicodin for pain",
        "IMPRESSION": "ACUTE DENTAL ABSCESS",
        "ASSESSMENT_AND_PLAN": "The patient needs to follow up with the dentist for definitive treatment and care. She is treated symptomatically at this time for the pain with a dental block as well as empirically with antibiotics. However, outpatient followup should be adequate. She is discharged in stable condition"
    },
    "Dental_Pain_Emergency_Visit": {

        "HISTORY_OF_PRESENT_ILLNESS": "This is a 45-year-old Caucasian female who states that starting last night she has had very significant pain in her left lower jaw. The patient states that she can feel an area with her tongue and one of her teeth that appears to be fractured. The patient states that the pain in her left lower teeth kept her up last night. The patient did go to Clinic but arrived there later than 7 a.m., so she was not able to be seen there will call line for dental care. The patient states that the pain continues to be very severe at 9/10. She states that this is like a throbbing heart beat in her left jaw. The patient denies fevers or chills. She denies purulent drainage from her gum line. The patient does believe that there may be an area of pus accumulating in her gum line however. The patient denies nausea or vomiting. She denies recent dental trauma to her knowledge",
        "PAST_MEDICAL_HISTORY": "1. Coronary artery disease.2. Hypertension.3. Hypothyroidism",
        "PAST_SURGICAL_HISTORY": "Coronary artery stent insertion",
        "SOCIAL_HABITS": "The patient denies alcohol or illicit drug usage. Currently she does have a history of tobacco abuse",
        "MEDICATIONS": "1. Plavix.2. Metoprolol.3. Synthroid.4. Potassium chloride",
        "ALLERGIES": "1. Penicillin. 2. Sulfa.",
        "PHYSICAL_EXAMINATION": "GENERAL: This is a Caucasian female who appears of stated age of 45 years. She is well-nourished, well-developed, in no acute distress. The patient is pleasant but does appear to be uncomfortable.VITAL SIGNS: Afebrile, blood pressure 145/91, pulse of 78, respiratory rate of 18, and pulse oximetry of 98% on room air.HEENT: Head is normocephalic. Pupils are equal, round and reactive to light and accommodation. Sclerae are anicteric and noninjected. Nares are patent and free of mucoid discharge. Mucous membranes are moist and free of exudate or lesion. Bilateral tympanic membranes are visualized and free of infection or trauma. Dentition shows significant decay throughout the dentition. The patient has had extraction of teeth 17, 18, and 19. The patient's tooth #20 does have a small fracture in the posterior section of the tooth and there does appear to be a very minor area of fluctuance and induration located at the alveolar margin at this site. There is no pus draining from the socket of the tooth. No other acute abnormality to the other dentition is visualized.",
        "DIAGNOSTIC_STUDIES": "None",
        "PROCEDURE_NOTE": "The patient does receive an injection of 1.5 mL of 0.5% bupivacaine for inferior alveolar nerve block on the left mandibular teeth. The patient undergoes this all procedure without complication and does report some mild decrease of her pain with this and patient was also given two Vicodin here in the Emergency Department and a dose of Keflex for treatment of her dental infection.",
        "ASSESSMENT": "Dental pain with likely dental abscess",
        "PLAN": "The patient was given a prescription for Vicodin. She is also given prescription for Keflex, as she is penicillin allergic. She has tolerated a dose of Keflex here in the Emergency Department well without hypersensitivity. The patient is strongly encouraged to follow up with Dental Clinic on Monday, and she states that she will do so. The patient verbalizes understanding of treatment plan and was discharged in satisfactory condition from the ER"
    },

    "Dental_Prophylaxis": {
        "PREOPERATIVE_DIAGNOSES": "1. Impacted wisdom teeth.2. Moderate gingivitis",
        "POSTOPERATIVE DIAGNOSES": "1. Impacted wisdom teeth 2. Moderate gingivitis.",
        "COMPLICATIONS": "None",
        "ESTIMATED_BLOOD_LOSS": "Minimal",
        "DURATION_OF_SURGERY": "One hour 17 minutes",
        "BRIEF_HISTORY": "The patient was referred to me by Dr. X. He contacted myself and stated that Angelica was going to have her wisdom teeth extracted in the setting of a hospital operating room at Hospital and he inquired if we could pair on the procedure and I could do her full mouth dental rehabilitation before the wisdom teeth were removed by him. I agreed. I saw her in my office and she was cooperative for full mouth set of radiographs in my office and a clinical examination. This clinical and radiographic examination revealed no dental caries; however, she was in need of a good dental cleaning",
        "OPERATIVE_PREPARATION": " The patient was brought to Hospital Day Surgery accompanied by her mother. I met with them and discussed the needs of the child, types of restoration to be performed, and the risks and benefits of the treatment as well as the options and alternatives of the treatment. After all their questions and concerns were addressed, they gave their informed consent to proceed with the treatment. The patient's history and physical examination was reviewed. Once she was cleared by Anesthesia, she was taken back to the operating room.",
        "OPERATIVE PROCEDURE": "The patient was placed on the surgical table in the usual supine position with all extremities protected. Anesthesia was induced by mask. The patient was then intubated with a nasal endotracheal tube and the tube was stabilized. The head was wrapped and the eyes were taped shut for protection. An Angiocath was previously placed in preop. The head and neck were draped in sterile towels, and the body was covered with lead apron and sterile sheath. A moist continuous throat pack was placed beyond tonsillar pillars. Plastic lip and cheek retractors were then placed. Preoperative digital intraoral photographs were taken. No digital radiographs were taken in the operating room, as I stated before I had a full set of digital radiographs taken in my office. A prophylaxis was then performed using a Prophy cup and fluoridated Prophy paste after scaling and replaning was done. She presented with moderate calculus on the buccal surfaces of her maxillary, first molars and lower molars. She did not require any restorative dentistry",
        "FINDINGS": "This patient presented in her permanent dentition. Her teeth #1, 16, 17, and 32 were impacted and are going to be removed following my full mouth dental rehabilitation by Dr. Alexander. Oral hygiene was fair. There was generalized plaque and calculus throughout. She did not have any caries, did not require any restorative dentistry",
        "CONCLUSION": "Following my dental surgery, the patient continued to intubated and was prepped for oral surgery procedures by Dr. X and his associates. There were no postop pain requirements. I did not have any specific requirements for the patient or her mother and that will be handled by Dr. X and their instructions on soft foods, etc., and pain control will be managed by them"
    },

    "Dental_Restoration": {
        "PREOPERATIVE_DIAGNOSIS": "Dental caries",
        "POSTOPERATIVE_DIAGNOSIS": "Dental caries",
        "PROCEDURE1": "Dental restoration",
        "CLINICAL_HISTORY": "This 2-year, 10-month-old male has not had any prior dental treatment because of his unmanageable behavior in a routine dental office setting. He was referred to me for that reason to be treated under general anesthesia for his dental work. Cavities have been noted by his parents and pediatrician that have been noted to be pretty severe. There are no contraindications to this procedure. He is healthy. His history and physical is in the chart",
        "PROCEDURE2": "The patient was brought to the operating room at 10:15 and placed in the supine position. Dr. X administered the general anesthetic after which 2 bite-wing and 2 periapical x-rays were exposed and developed and his teeth were examined. A throat pack was then placed. Tooth D had caries on the distal surface which was excavated and the tooth was restored with composite. Teeth E and F had caries in the mesial and distal surfaces, these carious lesions were excavated and the teeth were restored with composite. Tooth G had caries in the mesial surface which was excavated and the tooth was restored with composite. Teeth I and L both had caries on the occlusal surfaces which were excavated and upon excavation of the caries in tooth I the pulp was perforated and a therapeutic pulpotomy was therefore necessary. This was done using ferric sulfate and zinc oxide eugenol. For final restorations, amalgam restorations were placed involving the occlusal surfaces both teeth I and L. A prophylaxis was done and topical fluoride applied and the excess was suctioned thoroughly. The throat pack was removed and the patient was awakened and brought to the recovery room in good condition at 11:30. There was no blood loss"
    },

    "Bone_Impacted_Tooth_Removal": {
        "PREOPERATIVE_DIAGNOSIS": "Dentigerous cyst, left mandible associated with full bone impacted wisdom tooth #17",
        "POSTOPERATIVE_DIAGNOSIS": "Dentigerous cyst, left mandible associated with full bone impacted wisdom tooth #17",
        "PROCEDURE": "Removal of benign cyst and extraction of full bone impacted tooth #17",
        "ANESTHESIA": "General anesthesia with nasal endotracheal intubation",
        "SPECIMEN": "Cyst and section tooth #17",
        "ESTIMATED_BLOOD_LOSS": "10 mL",
        "FLUIDS": "1200 of Lactated Ringer's",
        "COMPLICATIONS": "None",
        "CONDITION": "The patient was extubated and transported to the PACU in good condition. Breathing spontaneously",
        "INDICATION_FOR_PROCEDURE": "The patient is a 38-year-old Caucasian male who was referred to clinic to evaluate a cyst in his left mandible. Preoperatively, a biopsy of the cyst was obtained and it was noted to be a benign dentigerous cyst.After evaluation of the location of the cyst and the impacted wisdom tooth approximately the inferior border of the mandible, it was determined that the patient would benefit from removal of the cyst and removal of tooth #17 under general anesthesia in the operating room. Risks, benefits, and alternatives of treatment were thoroughly discussed with the patient and consent was obtained",
        "DESCRIPTION_OF_PROCEDURE": "The patient was taken to the operating room #1 at Hospital and laid in the supine fashion on the operating room table. As stated, general anesthesia was induced with IV anesthetics and maintained with nasal endotracheal intubation and inhalation anesthetics. The patient was prepped and draped in usual oro-maxillofacial surgery fashion.Approximately, #6 mL of 2% lidocaine with 1:100,000 epinephrine was injected in the usual nerve block fashion. After waiting appropriate time for local anesthesia to take effect, a moistened Ray-Tec sponge was placed in the posterior pharynx. Peridex mouth rinse was used to prep the oral cavity. This was removed with suction.Using a #15 blade a sagittal split osteotomy incision was made along the left ramus. A full-thickness mucoperiosteal flap was elevated and the crest of the bone was identified where the crown had super-erupted since the biopsy 6 weeks earlier. Using a Hall drill, a buccal osteotomy was developed, the tooth was sectioned in half, fractured with an elevator and delivered in two pieces. Using a double-ended curette, the remainder of the cystic lining was removed from the left mandible and sent to pathology with the tooth for review.The area was irrigated with copious amounts of sterile water and closed with 3-0 chromic gut suture. The throat pack was removed. The procedure was then determined to be over, and the patient was extubated, breathing spontaneously, and transported to the PACU in good condition"

    },

    "Bony_Impacted_Teeth_Removal": {
        "PREOPERATIVE_DIAGNOSIS": "Completely bony impacted teeth #1, #16, #17, and #32",
        "POSTOPERATIVE_DIAGNOSIS": "Completely bony impacted teeth #1, #16, #17, and #32",
        "PROCEDURE": "Surgical removal of completely bony impacted teeth #1, #16, #17, and #32",
        "ANESTHESIA": "General nasotracheal",
        "COMPLICATIONS": "None",
        "CONDITION": "Stable to PACU",
        "DESCRIPTION_OF_PROCEDURE": "Patient was brought to the operating room, placed on the table in a supine position, and after demonstration of an adequate plane of general anesthesia via the nasotracheal route, patient was prepped and draped in the usual fashion for an intraoral procedure. A gauze throat pack was placed and local anesthetic was administered in all four quadrants, a total of 7.2 mL of lidocaine 2% with 1:100,000 epinephrine, and 3.6 mL of bupivacaine 0.5% with 1:200,000 epinephrine. Beginning on the upper right tooth #1, incision was made with a #15 blade. Envelope flap was raised with the periosteal elevator, and bone was removed on the buccal aspect with straight elevator. Potts elevator was then used to luxate the tooth from the socket. Remnants of the follicle were then removed with hemostat. The area was irrigated and then closed with 3-0 gut suture. On the lower right tooth #32, incision was made with a #15 blade. Envelope flap was raised with the periosteal elevator, and bone was removed on the buccal and distal aspect with a high-speed drill with a round bur. Tooth was then sectioned with the bur and removed in several pieces. Remnants of the follicle were removed with a curved hemostat. The area was irrigated with normal saline solution and closed with 3-0 gut sutures. Moving to #16 on the upper left, incision was made with a #15 blade. Envelope flap was raised with the periosteal elevator, and bone was removed on the buccal aspect with straight elevator. Potts elevator was then used to luxate the tooth from the socket. Remnants of the follicle were removed with a curved hemostat. The area was irrigated with normal saline solution and closed with 3-0 gut sutures. Moving to the lower left #17, incision was made with a #15 blade. Envelope flap was raised with the periosteal elevator, and bone was removed on the buccal and distal aspect with high-speed drill with a round bur. Then the bur was used to section the tooth vertically. Tooth was removed in several pieces followed by the removal of the remnants of the follicle. The area was irrigated with normal saline solution and closed with 3-0 gut sutures. Upon completion of the procedure, the throat pack was removed and the pharynx was suctioned. An NG tube was then inserted and small amount of gastric contents were suctioned. Patient was then awakened, extubated, and taken to the PACU in stable condition"
    },

    "Carious_Teeth_Extraction": {
        "PREOPERATIVE_DIAGNOSIS": "Carious teeth and periodontal disease affecting all remaining teeth",
        "POSTOPERATIVE_DIAGNOSIS": "Carious teeth and periodontal disease affecting all remaining teeth and partial bony impacted tooth #32",
        "PROCEDURE": "Extraction of remaining teeth numbers 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, and 32",
        "ANESTHESIA": "General, oral endotracheal",
        "COMPLICATIONS": "None",
        "CONDITION": "Stable to PACU; PROCEDURE: Patient was brought to the operating room, placed on the table in the supine position and after demonstration of an adequate plane of general anesthesia, the patient was prepped and draped in the usual fashion for an intraoral procedure. Gauze throat pack was placed and local anesthetic was administered in the upper and lower left quadrants and extraction of teeth was begun on the upper left quadrant teeth numbers 9, 10, 11, 12, 13, 14, 15, and 16 were removed with elevators and forceps extraction. Moving to the lower quadrant on the left side, tooth numbers 17, 18, 19, 20, 21, 22, 23, and 24 were removed with elevators and routine forceps extraction. The flaps were then closed with 3-0 gut sutures and upon completion of the two quadrants on the left side, the endotracheal tube was then relocated from the right side to the left side for access to the quadrants on the right. Teeth numbers 2, 3, 4, 5, 7, and 8 were then removed with elevators and routine forceps extraction. It was noted that tooth #6 was missing, could not be seen whether tooth #6 was palately impacted, but the tooth was not encountered. On the lower right quadrant, teeth numbers 25, 26, 27, 28, 29, 30, and 31 were removed with elevators and routine forceps extraction. Tooth #32 was partially bony impacted, but exposed, so it was removed by removing bone on buccal aspect with high-speed drill with a round bur. Tooth was then luxated from the socket. The flaps were then closed on both quadrants with 3-0 gut sutures. The area was irrigated thoroughly with normal saline solution and a total of 8.5 mL of lidocaine 2% with 1:100, 000 epinephrine and 3.6 mL of bupivacaine 0.5% with epinephrine 1:200, 000. Upon completion of the procedure, the throat pack was removed. The pharynx was suctioned. An oral gastric tube was passed and small amount of stomach contents were suctioned. The patient was then extubated and taken to PACU in stable condition. ",

    },

    "Closed_Reduction_Mandible_Fracture": {
        "PREOPERATIVE_DIAGNOSIS": "Bilateral open mandible fracture, open left angle and open symphysis fracture",
        "POSTOPERATIVE_DIAGNOSIS": "Bilateral open mandible fracture, open left angle and open symphysis fracture",
        "PROCEDURE": "Closed reduction of mandible fracture with MMF",
        "ANESTHESIA": "General anesthesia via nasal endotracheal intubation",
        "FLUIDS": "2 L of crystalloid",
        "ESTIMATED_BLOOD_LOSS": "Minimal",
        "HARDWARE": "None",
        "SPECIMENS": "None",
        "COMPLICATIONS": "None",
        "CONDITION": "The patient was extubated to PACU in good condition",
        "INDICATIONS_FOR_PROCEDURE": "The patient is a 17-year-old female who is 2 days status post an altercation in which she sustained multiple blows to the face. She was worked up on Friday night, 2 days earlier at Hospital, was given palliative treatment and discharged and instructed to follow up as an outpatient with an oral surgeon and given a phone number to call. The patient was worked up initially. On initial exam, it was noted that the patient had a left V3 paresthesia. She had a gross malocclusion. On the facial CT and panoramic x-ray, it was noted to be a displaced left angle fracture and nondisplaced symphysis fracture. Alternatives were discussed with the patient and it was determined she would benefit from being taken to the operating room under general anesthesia to have a closed reduction of her fractures. Risks, benefits, and alternatives of treatment were thoroughly discussed with the patient and informed consent was obtained with the patient's mother.",
        "DESCRIPTION_OF_PROCEDURE": "The patient was taken to the operating room #4 at Hospital and laid in a supine position on the operating room table. Monitor was attached and general anesthesia was induced with IV anesthetics and maintained with nasal endotracheal intubation and inhalation anesthetics. The patient was prepped and draped in the usual oromaxillofacial surgery fashion.Surgeon approached the operating table in a sterile fashion. Approximately 10 mL of 2% lidocaine with 1:100,000 epinephrine was injected into the oral vestibule in a nerve block fashion. A moistened Ray-Tec sponge was placed in the posterior oropharynx and the mouth was prepped with Peridex mouthrinse, scrubbed with a toothbrush. The Peridex was evacuated with Yankauer suction. Erich arch bars were adapted to the maxilla from the first molar to the contralateral first molar and secured with 24-gauge surgical steel wire on the posterior teeth and 26-gauge surgical steel wire on the anterior teeth. Same was done on the mandible. The patient was then manipulated up in the maximum intercuspation and noted to be reproducible. The throat pack was then removed.The patient was remanipulated up to the maximum intercuspation and secured with interdental elastics. At this point in time, the procedure was then determined to be over.The patient was extubated and transferred to the PACU in good condition."
    }
}

# create the corpus id to name mapping


# create English stop words list
en_stop = get_stopwords('en')

sentencelist = []
keylist = []
namelist = []
for key, value in TestData.items():
    for fieldkey, fieldvalue in value.items():
        sentencelist.append(fieldvalue)
        keylist.append(key + "+" + fieldkey)
        namelist.append(fieldkey)

# calculate the levenstein distance of the names:
nameListLength = len(namelist)
levdistanceList = []
for i in range(nameListLength):
    levdistanceListInner = []
    for j in range(nameListLength):
        levensteinValue = eval(namelist[i], namelist[j])
        levdistanceListInner.append(levensteinValue)
        levdistanceListInner = map(float, levdistanceListInner)
    levdistanceList.append(levdistanceListInner)

# print levdistanceList

# Classify the corpus based on the levenstein distance
levdistanceMat = np.mat(levdistanceList)

# weightForEach = 1 - 2*mat(levdistanceList)/amax(mat(levdistanceList),axis=0)[0]

# print amax(mat(levdistanceList),axis=0)
weightForEach = levdistanceMat / np.amax(levdistanceMat, axis=0)[0]
# print amin(weightForEach,axis=0)[0]

print weightForEach
texts = [[word for word in document.lower().split() if word not in en_stop]
         for document in sentencelist]

'''
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

# Only keep words that appear more than once
processed_corpus = [[token for token in text if frequency[token] > 1] for text in texts]
print processed_corpus
dictionary = corpora.Dictionary(processed_corpus)
print(dictionary.token2id)
bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]
print bow_corpus
tfidf_model = models.TfidfModel(bow_corpus)

corpus_tfidf = tfidf_model[bow_corpus]

lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=40)

#ldaOut=lda.print_topics(2)
#print ldaOut[0]
#print ldaOut[1]

#corpus_lda = lda[corpus_tfidf]
index = similarities.MatrixSimilarity(lda[bow_corpus])
print "################################"
for idx,corpus1 in enumerate(bow_corpus):
    simmatrix = index[lda[corpus1]]
    #print list(enumerate(simmatrix))
    sort_sims = sorted(enumerate(simmatrix), key=lambda item: item[1],reverse=True)
    result = [(keylist[tulple[0]],tulple[1]) for tulple in sort_sims]
    print keylist[idx]
    print result

'''

# Generate weighted tfidf model
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


# rewrite the tfidf function,return exactly same format as the gensim package
def df2idf(docfreq, totaldocs, log_base=2.0, add=0.0):
    return add + np.log(float(totaldocs) / docfreq) / np.log(log_base)


def TfidfCustom(corpus, query, queryFieldNo, normalize=matutils.unitvec):
    termid_array, tf_array = [], []
    for termid, tf in query:
        termid_array.append(termid)
        tf_array.append(tf)

    dfs = {}
    docno = -1

    for docno, bow in enumerate(corpus):

        for termid, _ in bow:
            if termid in termid_array:
                levdistanceweight = weightForEach[queryFieldNo, docno]
                dfs[termid] = dfs.get(termid, 0) + levdistanceweight

    # avoid devide 0
    idfs = {termid: df2idf(df + 1, docno + 1) for termid, df in iteritems(dfs)}

    vector = [
        (termid, tf * idfs.get(termid))
        for termid, tf in zip(termid_array, tf_array) if abs(idfs.get(termid, 0.0)) > 1e-12
    ]

    vector = normalize(vector)
    vector = [(termid, weight) for termid, weight in vector if abs(weight) > 1e-12]

    return vector


dictionary = corpora.Dictionary(texts)
print(dictionary.token2id)
bow_corpus = [dictionary.doc2bow(text) for text in texts]

# print TfidfCustom(bow_corpus,bow_corpus[0],0)
tfidf_model = models.TfidfModel(bow_corpus)

corpus_tfidf = tfidf_model[bow_corpus]

# TfidfCustom(bow_corpus,bow_corpus[70],70)
# print len(bow_corpus)


corpuslist = []
for i, j in enumerate(bow_corpus):
    corpuslist.append(TfidfCustom(bow_corpus, j, i))

# print corpuslist[0]


resultMap = {}

numLoops = 100
for i in range(numLoops):

    lda = models.LdaModel(corpuslist, id2word=dictionary, num_topics=2)
    # corpus_lda = lda[corpus_tfidf]
    index = similarities.MatrixSimilarity(lda[bow_corpus])
    # for idx,corpus1 in enumerate(bow_corpus):
    for idx in range(len(bow_corpus)):
        # print idx
        corpus1 = bow_corpus[idx]
        # print corpus1
        simmatrix = index[lda[corpus1]]
        # print list(enumerate(simmatrix))
        # sort_sims = sorted(enumerate(simmatrix), key=lambda item: item[1],reverse=True)
        result = [(keylist[tulple[0]], tulple[1]) for tulple in enumerate(simmatrix)]
        if i == 0:
            resultMap[keylist[idx]] = result
        else:
            resultMap[keylist[idx]] = map(lambda x, y: (x[0], x[1] + y[1]), resultMap[keylist[idx]], result)

for key, value in resultMap.iteritems():
    # print key,value
    resultMap[key] = map(lambda x: (x[0], x[1] / numLoops), value)

# print resultMap
# resultMap = map(lambda x:(x[0],x[1]/numLoops),enumerate(resultMap.items()))
# print resultMap
# print resultMap
for key, value in resultMap.iteritems():
    resultMap[key] = sorted(value, key=lambda item: item[1], reverse=True)
# print sort_sims
print resultMap

print "################################"

resultMap = {}

numLoops = 100
for i in range(numLoops):

    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=2)
    # corpus_lda = lda[corpus_tfidf]
    index = similarities.MatrixSimilarity(lda[bow_corpus])
    # for idx,corpus1 in enumerate(bow_corpus):
    for idx in range(len(bow_corpus)):
        # print idx
        corpus1 = bow_corpus[idx]
        # print corpus1
        simmatrix = index[lda[corpus1]]
        # print list(enumerate(simmatrix))
        # sort_sims = sorted(enumerate(simmatrix), key=lambda item: item[1],reverse=True)
        result = [(keylist[tulple[0]], tulple[1]) for tulple in enumerate(simmatrix)]
        if i == 0:
            resultMap[keylist[idx]] = result
        else:
            resultMap[keylist[idx]] = map(lambda x, y: (x[0], x[1] + y[1]), resultMap[keylist[idx]], result)

            # resultmap[keylist[tulple[0]]]
# print resultMap

for key, value in resultMap.iteritems():
    # print key,value
    resultMap[key] = map(lambda x: (x[0], x[1] / numLoops), value)

# print resultMap
# resultMap = map(lambda x:(x[0],x[1]/numLoops),enumerate(resultMap.items()))
# print resultMap
# print resultMap
for key, value in resultMap.iteritems():
    resultMap[key] = sorted(value, key=lambda item: item[1], reverse=True)
# print sort_sims
print resultMap

'''
lda = models.LdaModel(corpuslist, id2word=dictionary, num_topics=40)
#corpus_lda = lda[corpus_tfidf]
index = similarities.MatrixSimilarity(lda[bow_corpus])
print "################################"
for i,j in enumerate(index):
    print i
    print j
#print index
print "################################"
for idx,corpus1 in enumerate(bow_corpus):
    print "5555555555555555555555555555"
    print corpus1
    print "6666666666666666666666666666"
    print lda[corpus1]
    print "::::::::::::::::::::::::::::"
    for kk in lda[corpus1]:
        print kk
    print "7777777777777777777777777777"
    print index[lda[corpus1]]
    print "5555555555555555555555555555"
    #simmatrix = index[lda[corpus1]]
    simmatrix = index[lda[corpus1]]
    #print list(enumerate(simmatrix))
    sort_sims = sorted(enumerate(simmatrix), key=lambda item: item[1],reverse=True)
    result = [(keylist[tulple[0]],tulple[1]) for tulple in sort_sims]
    print keylist[idx]
    print result


'''

'''
#print texts
#print len(texts)
print [texts[0],texts[0]]
for i in range(len(texts)-1):
    total_corpus_tfidf = []
    for j in range(len(texts)-1):
        if (i == j):
            corporaEach = [texts[i],texts[j]]
            #print corporaEach
            #print texts[i]
            dictionary = corpora.Dictionary(corporaEach)
            bow_corpus = [dictionary.doc2bow(text) for text in corporaEach]
            tfidf_model = models.TfidfModel(bow_corpus)
            corpus_tfidf = tfidf_model[bow_corpus[0]]
            #weighted_corpus_tfidf = map(lambda x:,corpus_tfidf)
            #if (i != j):
            #total_corpus_tfidf = map(lambda x,y:(x[0] or y[0],x[1]+y[1]),corpus_tfidf,total_corpus_tfidf)
            print corpus_tfidf

    print len(total_corpus_tfidf)
'''
