import pymongo
import time

uri = 'mongodb://localhost/local'

client = pymongo.MongoClient(uri)

db = client.get_database()

sourcedb1 = db['sourcedb1']

sourcedb2 = db['sourcedb2']

sourcedb3 = db['sourcedb3']



'''
data1 = {"aaa":"111","bbb":"222","ccc":"333","ddd":"444","eee":"555","fff":"666","ggg":"777","hhh":"888"}

data2 = {"aaa":"222","bbb":"333","ccc":"444","ddd":"555"}

for i in range(1,400):
    #sourcedb1.insert_one(data1.copy())
    #time.sleep(1)
    sourcedb2.insert_one(data2.copy())


'''



SEED_DATA1 = [
    {
        "Username": "Heinrich Volkmann",
        "Userid": "A012233344RF",
        "Useremail": "hvman@gmail.com",
        #"Prescriptiontype": "Dental Pain",
        "Date": "2016 06 06",
        "Bone_Impacted_Tooth_Removal": "Dentigerous cyst, left mandible associated with full bone impacted wisdom tooth #17. Removal of benign cyst and extraction of full bone impacted tooth #17",
        "Bony_Impacted_Teeth_Removal": "Surgical removal of completely bony impacted teeth",
        "Carious_Teeth_Extraction": "Carious teeth and periodontal disease affecting all remaining teeth and partial bony impacted tooth #32. Extraction of teet",
        "History_of_Illness": "This is a 27-year-old female who presents with a couple of days history of some dental pain. She has had increasing swelling and pain to the left lower mandible area today.",
        "Closed_Reduction_Mandible_Fracture": 250,
        "vOffset": 100,
        "alignment": "center",
        "onMouseUp": "sun1.opacity = (sun1.opacity / 100) * 90"

    },
    {
        "Username": "Heinz Guncher",
        "Userid": "R30086892WED",
        "Useremail": "hgunz@gmail.com",
        #"Prescriptiontype": "Dental Pain",
        "Date": "2016 08 11",
        "Bone_Impacted_Tooth_Removal": "Dentigerous cyst, right mandible associated with full bone impacted wisdom tooth #20. Removal of benign cyst and extraction of full bone impacted tooth #20",
        "Bony_Impacted_Teeth_Removal": "Surgical need to remove teeth bones",
        "Carious_Teeth_Extraction": "Carious teeth and periodontal disease affecting all remaining teeth and partial bony impacted tooth #23. Extraction of teet",
        "History_of_Illness": "This is a 56-year-old male who presents with a couple of days history of some dental pain. She has had increasing swelling and pain to the left lower mandible area today.",
        "Closed_Reduction_Mandible_Fracture": 250,
        "vOffset": 50,
        "alignment": "left",
        "onMouseUp": "sun1.opacity = (sun1.opacity / 100) * 90"
    }

]


SEED_DATA2 = [
    {
        "UserName": "Heinrich Volkmann",
        "UserId": "A012233344RF",
        "Date": "2016 06 06",
        "UserEmail": "hvman@gmail.com",
        #"PrescriptionType": "Abdominal Exploration",
        "Description": "Congenital chylous ascites and chylothorax and rule out infradiaphragmatic lymphatic leak. Diffuse intestinal and mesenteric lymphangiectasia",
        "POSTOPERATIVE_DIAGNOSES": "1. Congenital chylous ascites and chylothorax. 2. Rule out infradiaphragmatic lymphatic leak.",
        "ANESTHESIA": "General",
        "INDICATION": "The patient is an unfortunate 6-month-old baby boy, who has been hospitalized most of his life with recurrent chylothoraces and chylous ascites. The patient has been treated somewhat successfully with TPN and voluntary restriction of enteral nutrition, but he had repeated chylothoraces. Last week, Dr. X took the patient to the operating room in hopes that with thoracotomy, a thoracic duct leak could be found, which would be successfully closed surgically. However at the time of his thoracotomy exploration what was discovered was a large amount of transdiaphragmatic transition of chylous ascites coming from the abdomen. Dr. X opened the diaphragm and could literally see a fountain of chylous fluid exiting through the diaphragmatic hole. This was closed, and we decided that perhaps an abdominal exploration as a last stage effort would allow us to find an area of lymphatic leak that could potentially help the patient from this dismal prognostic disease. We met with his parents and talked to them about this, and he is here today for that attempt.",
        "OPERATIVE_FINDINGS": "The patient's abdomen was relatively soft, minimally distended. Exploration through supraumbilical transverse incision immediately revealed a large amount of chylous ascites upon entering into the peritoneal cavity. What we found which explains the chronic chylous ascites and chylothorax was a diffuse lymphangiectatic picture involving the small bowel mesentery approximately two thirds to three quarters of the distal small bowel including all of the ileum, the cecum, and the portion of the ascending colon. It appeared that any attempt to resect this area would have been met with failure because of the extensive lymphatic dilatation all the way down towards the root of the supramesenteric artery. There was about one quarter to one third of the jejunum that did not appear to be grossly involved, but I did not think that resection of three quarters of the patient's small bowel would be viable surgical option. Instead, we opted to close his abdomen and refer for potential small intestine transplantation procedure in the future if he is a candidate for that.The lymphatic abnormality was extensive. They were linear dilated lymphatic channels on the serosal surface of the bowel in the mesentery. They were small aneurysm-like pockets of chyle all along the course of the mesenteric structures and in the mesentery medially adjacent to the bowel as well. No other major retroperitoneal structure or correctable structure was identified. Both indirect inguinal hernias were wide open and could be palpated from an internal aspect as well.",
        "DESCRIPTION_OF_OPERATION": "The patient was brought from the Pediatric Intensive Care Unit to the operating room within an endotracheal tube im place and with enteral feeds established at full flow to provide maximum fat content and maximum lymphatic flow. We conducted a surgical time-out and reiterated all of the patient's important identifying information and confirmed the operative plan as described above. Preparation and draping of his abdomen was done with chlorhexidine based prep solution and then we opened his peritoneal cavity through a transverse supraumbilical incision dividing both rectus muscles and all layers of the abdominal wall fascia. As the peritoneal cavity was entered, we divided the umbilical vein ligamentum teres remnant between Vicryl ties, and we were able to readily identify a large amount of chylous ascites that had been previously described. The bowel was eviscerated, and then with careful inspection, we were able to identify this extensive area of intestinal and mesenteric lymphangiectasia that was a source of the patient's chylous ascites. The small bowel from the ligament of Treitz to the proximal to mid jejunum was largely unaffected, but did not appear that resection of 75% of the small intestine and colon would be a satisfactory tradeoff for The patient, but would likely render him with significant short bowel and nutritional and metabolic problems. Furthermore, it might burn bridges necessary for consideration of intestinal transplantation in the future if that becomes an option. We suctioned free all of the chylous accumulations, replaced the intestines to their peritoneal cavity, and then closed the patient's abdominal incision with 4-0 PDS on the posterior sheath and 3-0 PDS on the anterior rectus sheath. Subcuticular 5-0 Monocryl and Steri-Strips were used for skin closure. The patient tolerated the procedure well. He lost minimal blood, but did lose approximately 100 mL of chylous fluid from the abdomen that was suctioned free as part of the chylous ascitic leak. The patient was returned to the Pediatric Intensive Care Unit with his endotracheal tube in place and to consider the next stage of management, which might be an attempted additional type of feeding or referral to an Intestinal Transplantation Center to see if that is an option for the patient because he has no universally satisfactory medical or surgical treatment for this at this time. "

    },
    {
        "UserName": "Alex Munster",
        "UserId": "F19390202SDE",
        "Date": "2016 06 06",
        "UserEmail": "alexMunc@hotmail.com",
        #"PrescriptionType": "Abdominal Exploration",
        "Description": "Congenital chylous ascites and chylothorax and rule out infradiaphragmatic lymphatic leak. Diffuse intestinal and mesenteric lymphangiectasia",
        "POSTOPERATIVE_DIAGNOSES": "1. Rule out infradiaphragmatic lymphatic leak.",
        "ANESTHESIA": "General",
        "INDICATION": "The patient is a 59 years old man, who has been hospitalized most of his life with recurrent chylothoraces and chylous ascites. The patient has been treated somewhat successfully with TPN and voluntary restriction of enteral nutrition, but he had repeated chylothoraces. Last week, Dr. X took the patient to the operating room in hopes that with thoracotomy, a thoracic duct leak could be found, which would be successfully closed surgically. However at the time of his thoracotomy exploration what was discovered was a large amount of transdiaphragmatic transition of chylous ascites coming from the abdomen. Dr. X opened the diaphragm and could literally see a fountain of chylous fluid exiting through the diaphragmatic hole. This was closed, and we decided that perhaps an abdominal exploration as a last stage effort would allow us to find an area of lymphatic leak that could potentially help the patient from this dismal prognostic disease. We met with his parents and talked to them about this, and he is here today for that attempt.",
        "OPERATIVE_FINDINGS": "The patient's abdomen was relatively soft, minimally distended. Exploration through supraumbilical transverse incision immediately revealed a large amount of chylous ascites upon entering into the peritoneal cavity. What we found which explains the chronic chylous ascites and chylothorax was a diffuse lymphangiectatic picture involving the small bowel mesentery approximately two thirds to three quarters of the distal small bowel including all of the ileum, the cecum, and the portion of the ascending colon. It appeared that any attempt to resect this area would have been met with failure because of the extensive lymphatic dilatation all the way down towards the root of the supramesenteric artery. There was about one quarter to one third of the jejunum that did not appear to be grossly involved, but I did not think that resection of three quarters of the patient's small bowel would be viable surgical option. Instead, we opted to close his abdomen and refer for potential small intestine transplantation procedure in the future if he is a candidate for that.The lymphatic abnormality was extensive. They were linear dilated lymphatic channels on the serosal surface of the bowel in the mesentery. They were small aneurysm-like pockets of chyle all along the course of the mesenteric structures and in the mesentery medially adjacent to the bowel as well. No other major retroperitoneal structure or correctable structure was identified. Both indirect inguinal hernias were wide open and could be palpated from an internal aspect as well.",
        "DESCRIPTION_OF_OPERATION": "The patient was brought from the Pediatric Intensive Care Unit to the operating room within an endotracheal tube im place and with enteral feeds established at full flow to provide maximum fat content and maximum lymphatic flow. We conducted a surgical time-out and reiterated all of the patient's important identifying information and confirmed the operative plan as described above. Preparation and draping of his abdomen was done with chlorhexidine based prep solution and then we opened his peritoneal cavity through a transverse supraumbilical incision dividing both rectus muscles and all layers of the abdominal wall fascia. As the peritoneal cavity was entered, we divided the umbilical vein ligamentum teres remnant between Vicryl ties, and we were able to readily identify a large amount of chylous ascites that had been previously described. The bowel was eviscerated, and then with careful inspection, we were able to identify this extensive area of intestinal and mesenteric lymphangiectasia that was a source of the patient's chylous ascites. The small bowel from the ligament of Treitz to the proximal to mid jejunum was largely unaffected, but did not appear that resection of 75% of the small intestine and colon would be a satisfactory tradeoff for The patient, but would likely render him with significant short bowel and nutritional and metabolic problems. Furthermore, it might burn bridges necessary for consideration of intestinal transplantation in the future if that becomes an option. We suctioned free all of the chylous accumulations, replaced the intestines to their peritoneal cavity, and then closed the patient's abdominal incision with 4-0 PDS on the posterior sheath and 3-0 PDS on the anterior rectus sheath. Subcuticular 5-0 Monocryl and Steri-Strips were used for skin closure. The patient tolerated the procedure well. He lost minimal blood, but did lose approximately 100 mL of chylous fluid from the abdomen that was suctioned free as part of the chylous ascitic leak. The patient was returned to the Pediatric Intensive Care Unit with his endotracheal tube in place and to consider the next stage of management, which might be an attempted additional type of feeding or referral to an Intestinal Transplantation Center to see if that is an option for the patient because he has no universally satisfactory medical or surgical treatment for this at this time. "

    },
    {
        "UserName": "Jakob Bosterz",
        "UserId": "T302930294CED",
        "Date": "2016 06 06",
        "UserEmail": "jakobBo@gmail.com",
        #"PrescriptionType": "Abdominal Exploration",
        "Description": "Congenital chylous ascites and chylothorax and rule out infradiaphragmatic lymphatic leak. Diffuse intestinal and mesenteric lymphangiectasia",
        "POSTOPERATIVE_DIAGNOSES": "1. Congenital chylous ascites and chylothorax. 2. Rule out infradiaphragmatic lymphatic leak.",
        "ANESTHESIA": "General",
        "INDICATION": "The patient is a 35-year-old man, who has been hospitalized most of his life with recurrent chylothoraces and chylous ascites. The patient has been treated somewhat successfully with TPN and voluntary restriction of enteral nutrition, but he had repeated chylothoraces. Last week, Dr. X took the patient to the operating room in hopes that with thoracotomy, a thoracic duct leak could be found, which would be successfully closed surgically. However at the time of his thoracotomy exploration what was discovered was a large amount of transdiaphragmatic transition of chylous ascites coming from the abdomen. Dr. X opened the diaphragm and could literally see a fountain of chylous fluid exiting through the diaphragmatic hole. This was closed, and we decided that perhaps an abdominal exploration as a last stage effort would allow us to find an area of lymphatic leak that could potentially help the patient from this dismal prognostic disease. We met with his parents and talked to them about this, and he is here today for that attempt.",
        "OPERATIVE_FINDINGS": "The patient's abdomen was relatively soft, minimally distended. Exploration through supraumbilical transverse incision immediately revealed a large amount of chylous ascites upon entering into the peritoneal cavity. What we found which explains the chronic chylous ascites and chylothorax was a diffuse lymphangiectatic picture involving the small bowel mesentery approximately two thirds to three quarters of the distal small bowel including all of the ileum, the cecum, and the portion of the ascending colon. It appeared that any attempt to resect this area would have been met with failure because of the extensive lymphatic dilatation all the way down towards the root of the supramesenteric artery. There was about one quarter to one third of the jejunum that did not appear to be grossly involved, but I did not think that resection of three quarters of the patient's small bowel would be viable surgical option. Instead, we opted to close his abdomen and refer for potential small intestine transplantation procedure in the future if he is a candidate for that.The lymphatic abnormality was extensive. They were linear dilated lymphatic channels on the serosal surface of the bowel in the mesentery. They were small aneurysm-like pockets of chyle all along the course of the mesenteric structures and in the mesentery medially adjacent to the bowel as well. No other major retroperitoneal structure or correctable structure was identified. Both indirect inguinal hernias were wide open and could be palpated from an internal aspect as well.",
        "DESCRIPTION_OF_OPERATION": "The patient was brought from the Pediatric Intensive Care Unit to the operating room within an endotracheal tube im place and with enteral feeds established at full flow to provide maximum fat content and maximum lymphatic flow. We conducted a surgical time-out and reiterated all of the patient's important identifying information and confirmed the operative plan as described above. Preparation and draping of his abdomen was done with chlorhexidine based prep solution and then we opened his peritoneal cavity through a transverse supraumbilical incision dividing both rectus muscles and all layers of the abdominal wall fascia. As the peritoneal cavity was entered, we divided the umbilical vein ligamentum teres remnant between Vicryl ties, and we were able to readily identify a large amount of chylous ascites that had been previously described. The bowel was eviscerated, and then with careful inspection, we were able to identify this extensive area of intestinal and mesenteric lymphangiectasia that was a source of the patient's chylous ascites. The small bowel from the ligament of Treitz to the proximal to mid jejunum was largely unaffected, but did not appear that resection of 75% of the small intestine and colon would be a satisfactory tradeoff for The patient, but would likely render him with significant short bowel and nutritional and metabolic problems. Furthermore, it might burn bridges necessary for consideration of intestinal transplantation in the future if that becomes an option. We suctioned free all of the chylous accumulations, replaced the intestines to their peritoneal cavity, and then closed the patient's abdominal incision with 4-0 PDS on the posterior sheath and 3-0 PDS on the anterior rectus sheath. Subcuticular 5-0 Monocryl and Steri-Strips were used for skin closure. The patient tolerated the procedure well. He lost minimal blood, but did lose approximately 100 mL of chylous fluid from the abdomen that was suctioned free as part of the chylous ascitic leak. The patient was returned to the Pediatric Intensive Care Unit with his endotracheal tube in place and to consider the next stage of management, which might be an attempted additional type of feeding or referral to an Intestinal Transplantation Center to see if that is an option for the patient because he has no universally satisfactory medical or surgical treatment for this at this time. "

    }
]



#Dental_Sugery
SEED_DATA3 = [
    {
        "User_Name": "Hermann Reinhert",
        "User_Id": "A53392422RT",
        "User_Email": "hein@gmail.com",
        #"Prescriptiontype": "Dental Pain",
        "Sugery_Steps":"Clean the teeth, Remove teech for #1,#3 #5. Use anaesthetic for surgery",
        "Date": "2016 08 12",
        "Carious_Teeth_Extraction": "Carious teeth and periodontal disease affecting left of all remaining teeth ",
        "History_of_Illness": "This is a 29-year-old male who presents with a couple of days history of some dental pain. She has had increasing swelling and need to do the sugery for now.",
        "alignment": "left"

    },
    {
        "User_Name": "Nina Merz",
        "User_Id": "H435333343GH",
        "User_Email": "nmerz@hotmail.com",
        #"Prescriptiontype": "Dental Pain",
        "Sugery_Steps":"Clean the teeth, Remove teech for #7,#8 #9. Use anaesthetic for surgery",
        "Date": "2016 08 15",
        "Carious_Teeth_Extraction": "Carious teeth and periodontal disease affecting all remaining teeth and partial bony impacted tooth #23. Extraction of teet",
        "History_of_Illness": "This is a 56-year-old female who presents with a couple of days history of some dental pain. She has had increasing swelling and pain to the left lower mandible area today.",
        "alignment": "left"
    }

]


#sourcedb3.insert_many(SEED_DATA3)
#sourcedb2.insert_many(SEED_DATA2)
sourcedb1.insert_many(SEED_DATA1)