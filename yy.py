import logging
import random
import os
import threading
from flask import Flask # አዲስ መጨመሪያ
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. የአስማት ቁልፎች
TOKEN = "8814685966:AAGitN24CD-sWQXcybDu9bQjeNuC5OznjDQ"
ADMIN_ID = 7986264215

# --- ለ Render እንዳይተኛ የምንጨምረው 'የደወል' ክፍል ---
app = Flask('')
@app.route('/')
def home():
    return "እኔ ቦቱ ነኝ፣ አልተኛሁም!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)
# ---------------------------------------------

PAID_USERS_FILE = "paid_users.txt"

def get_paid_users():
    if not os.path.exists(PAID_USERS_FILE):
        return []
    with open(PAID_USERS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def add_paid_user(user_id):
    with open(PAID_USERS_FILE, "a") as f:
        f.write(f"{user_id}\n")

# ... (እዚህ ጋር ያሉት 100 ጥያቄዎች እንዳሉ ይቆያሉ) ...
EXAMS = {
    'Management': [
        {'q': '1. የአመራር የመጀመሪያው ተግባር ምንድነው?', 'o': ['ሀ. መቆጣጠር', 'ለ. ማቀድ', 'ሐ. መቅጠር'], 'a': 'ለ. ማቀድ'},
        {'q': '2. የሳይንሳዊ አመራር አባት ማን ነው?', 'o': ['ሀ. Frederick Taylor', 'ለ. Henry Fayol', 'ሐ. Max Weber'], 'a': 'ሀ. Frederick Taylor'},
        {'q': '3. በድርጅት ውስጥ ከፍተኛው የአመራር አካል?', 'o': ['ሀ. Top Management', 'ለ. Middle Management', 'ሐ. First Line'], 'a': 'ሀ. Top Management'},
        {'q': '4. ሰራተኛን ማበረታታት ምን ይባላል?', 'o': ['ሀ. Controlling', 'ለ. Motivation', 'ሐ. Planning'], 'a': 'ለ. Motivation'},
        {'q': '5. SWOT ውስጥ "W" ምንን ይወክላል?', 'o': ['ሀ. Work', 'ለ. Weakness', 'ሐ. Winner'], 'a': 'ለ. Weakness'},
        {'q': '6. የአመራር ጥበብ (Art) ነው ወይስ ሳይንስ?', 'o': ['ሀ. ጥበብ ብቻ', 'ለ. ሳይንስ ብቻ', 'ሐ. ሁለቱም'], 'a': 'ሐ. ሁለቱም'},
        {'q': '7. ሪፖርት ማዘጋጀት የትኛው ተግባር ነው?', 'o': ['ሀ. Controlling', 'ለ. Planning', 'ሐ. Organizing'], 'a': 'ሀ. Controlling'},
        {'q': '8. አንድ ስራ አስኪያጅ ሊኖረው የሚገባ ክህሎት?', 'o': ['ሀ. Technical', 'ለ. Human', 'ሐ. ሁሉም'], 'a': 'ሐ. ሁሉም'},
        {'q': '9. ስልጣንን ለሌላ ሰው ማካፈል?', 'o': ['ሀ. Delegation', 'ለ. Motivation', 'ሐ. Training'], 'a': 'ሀ. Delegation'},
        {'q': '10. ውጤታማነት (Effectiveness) ምንድነው?', 'o': ['ሀ. ግብን ማሳካት', 'ለ. ወጪ መቀነስ', 'ሐ. መቸኮል'], 'a': 'ሀ. ግብን ማሳካት'},
        {'q': '11. ሰራተኞችን የመመልመል ሂደት?', 'o': ['ሀ. Recruitment', 'ለ. Planning', 'ሐ. Firing'], 'a': 'ሀ. Recruitment'},
        {'q': '12. ድርጅቱ ለምን ይኖራል? የሚለው ጥያቄ መልስ?', 'o': ['ሀ. Mission', 'ለ. Vision', 'ሐ. Profit'], 'a': 'ሀ. Mission'},
        {'q': '13. የወደፊት ራዕይ የሚገልጸው?', 'o': ['ሀ. Vision', 'ለ. Mission', 'ሐ. Budget'], 'a': 'ሀ. Vision'},
        {'q': '14. የአስር አመት እቅድ ምን ይባላል?', 'o': ['ሀ. Short term', 'ለ. Long term', 'ሐ. Daily'], 'a': 'ለ. Long term'},
        {'q': '15. ግጭትን መፍታት የአመራር ሚና ነው?', 'o': ['ሀ. አዎ', 'ለ. አይደለም', 'ሐ. አንዳንዴ'], 'a': 'ሀ. አዎ'},
        {'q': '16. የሰዎች ፍላጎት ደረጃ (Hierarchy of needs)?', 'o': ['ሀ. Maslow', 'ለ. Taylor', 'ሐ. Smith'], 'a': 'ሀ. Maslow'},
        {'q': '17. "Laissez-faire" ምን አይነት አመራር ነው?', 'o': ['ሀ. ጥብቅ', 'ለ. ነፃ ተለቀቅ', 'ሐ. ዲሞክራሲያዊ'], 'a': 'ለ. ነፃ ተለቀቅ'},
        {'q': '18. ስራን መከፋፈል (Division of labor) ጥቅሙ?', 'o': ['ሀ. ስራ መናቅ', 'ለ. ውጤታማነት', 'ሐ. ድካም'], 'a': 'ለ. ውጤታማነት'},
        {'q': '19. "Total Quality Management" አህጽሮት?', 'o': ['ሀ. TQM', 'ለ. TMQ', 'ሐ. QMT'], 'a': 'ሀ. TQM'},
        {'q': '20. በስራ ቦታ መመሪያ መስጠት?', 'o': ['ሀ. Directing', 'ለ. Planning', 'ሐ. Staffing'], 'a': 'ሀ. Directing'},
        {'q': '21. መሪ እና ስራ አስኪያጅ አንድ ናቸው?', 'o': ['ሀ. አዎ', 'ለ. ልዩነት አላቸው', 'ሐ. አይታወቅም'], 'a': 'ለ. ልዩነት አላቸው'},
        {'q': '22. በቡድን መስራት ጥቅሙ?', 'o': ['ሀ. ስራን ያከብዳል', 'ለ. ውጤት ይጨምራል', 'ሐ. ጊዜ ይፈጃል'], 'a': 'ለ. ውጤት ይጨምራል'},
        {'q': '23. ውሳኔ የመወሰን ሂደት?', 'o': ['ሀ. Decision making', 'ለ. Organizing', 'ሐ. Controlling'], 'a': 'ሀ. Decision making'},
        {'q': '24. የድርጅት ህልውና የሚያረጋግጠው?', 'o': ['ሀ. ትርፍ', 'ለ. ወጪ', 'ሐ. ስብሰባ'], 'a': 'ሀ. ትርፍ'},
        {'q': '25. የሰው ሀብት አመራር አህጽሮት?', 'o': ['ሀ. HRM', 'ለ. HMR', 'ሐ. MHR'], 'a': 'ሀ. HRM'},
        {'q': '26. "Unity of Command" ማለት?', 'o': ['ሀ. ከሁለት ሰው ትእዛዝ መቀበል', 'ለ. ከአንድ አለቃ ብቻ መቀበል', 'ሐ. ያለ አለቃ መስራት'], 'a': 'ለ. ከአንድ አለቃ ብቻ መቀበል'},
        {'q': '27. የስራ አፈጻጸም መገምገም?', 'o': ['ሀ. Performance Appraisal', 'ለ. Hiring', 'ሐ. Planning'], 'a': 'ሀ. Performance Appraisal'},
        {'q': '28. የድርጅት መዋቅር?', 'o': ['ሀ. Organizational Structure', 'ለ. Building', 'ሐ. Roadmap'], 'a': 'ሀ. Organizational Structure'},
        {'q': '29. "First-line managers" እነማን ናቸው?', 'o': ['ሀ. ሱፐርቫይዘሮች', 'ለ. ዋና ስራ አስኪያጆች', 'ሐ. ዳይሬክተሮች'], 'a': 'ሀ. ሱፐርቫይዘሮች'},
        {'q': '30. በስራ ቦታ ስነ-ምግባር?', 'o': ['ሀ. Business Ethics', 'ለ. Profit', 'ሐ. Marketing'], 'a': 'ሀ. Business Ethics'},
        {'q': '31. የመረጃ ልውውጥ?', 'o': ['ሀ. Communication', 'ለ. Transport', 'ሐ. Coding'], 'a': 'ሀ. Communication'},
        {'q': '32. የገንዘብ እቅድ?', 'o': ['ሀ. Budget', 'ለ. Receipt', 'ሐ. Loan'], 'a': 'ሀ. Budget'},
        {'q': '33. "Staffing" ምንድነው?', 'o': ['ሀ. ሰራተኛ መቅጠር', 'ለ. እቃ መግዛት', 'ሐ. ሪፖርት መስራት'], 'a': 'ሀ. ሰራተኛ መቅጠር'},
        {'q': '34. የለውጥ አመራር?', 'o': ['ሀ. Change Management', 'ለ. Time Management', 'ሐ. Self Management'], 'a': 'ሀ. Change Management'},
        {'q': '35. ጊዜን በአግባቡ መጠቀም?', 'o': ['ሀ. Time Management', 'ለ. Goal setting', 'ሐ. Laziness'], 'a': 'ሀ. Time Management'},
        {'q': '36. አዲስ ሀሳብ ማመንጨት?', 'o': ['ሀ. Innovation', 'ለ. Copying', 'ሐ. Reading'], 'a': 'ሀ. Innovation'},
        {'q': '37. የደንበኞች እርካታ?', 'o': ['ሀ. Customer Satisfaction', 'ለ. Sales', 'ሐ. Income'], 'a': 'ሀ. Customer Satisfaction'},
        {'q': '38. "Theory X" ሰራተኛን እንዴት ያያል?', 'o': ['ሀ. ስራ የሚወድ', 'ለ. ስራ የሚጠላ', 'ሐ. ጎበዝ'], 'a': 'ለ. ስራ የሚጠላ'},
        {'q': '39. "Theory Y" ሰራተኛን እንዴት ያያል?', 'o': ['ሀ. ሀላፊነት የሚወድ', 'ለ. ሰነፍ', 'ሐ. የማይታመን'], 'a': 'ሀ. ሀላፊነት የሚወድ'},
        {'q': '40. ድርጅቱ ያለበትን ሁኔታ ማወቅ?', 'o': ['ሀ. Situational Analysis', 'ለ. Sleeping', 'ሐ. Dreaming'], 'a': 'ሀ. Situational Analysis'},
        {'q': '41. የአጭር ጊዜ እቅድ?', 'o': ['ሀ. Operational plan', 'ለ. Strategic plan', 'ሐ. Global plan'], 'a': 'ሀ. Operational plan'},
        {'q': '42. "Corporate Social Responsibility"?', 'o': ['ሀ. CSR', 'ለ. CRS', 'ሐ. SRC'], 'a': 'ሀ. CSR'},
        {'q': '43. የአመራር ክህሎትን ማሳደግ?', 'o': ['ሀ. Training', 'ለ. Playing', 'ሐ. Eating'], 'a': 'ሀ. Training'},
        {'q': '44. የድርጅት ሰነድ?', 'o': ['ሀ. Documentation', 'ለ. Paper', 'ሐ. Bin'], 'a': 'ሀ. Documentation'},
        {'q': '45. ስራን በወቅቱ መጨረስ?', 'o': ['ሀ. Punctuality', 'ለ. Delay', 'ሐ. Absent'], 'a': 'ሀ. Punctuality'},
        {'q': '46. "Organizing" ውስጥ የሚካተተው?', 'o': ['ሀ. ስራ መከፋፈል', 'ለ. መተኛት', 'ሐ. መከራከር'], 'a': 'ሀ. ስራ መከፋፈል'},
        {'q': '47. የውሳኔ አሰጣጥ ሞዴል?', 'o': ['ሀ. Rational model', 'ለ. Random model', 'ሐ. No model'], 'a': 'ሀ. Rational model'},
        {'q': '48. የድርጅት አላማ?', 'o': ['ሀ. Goal', 'ለ. Street', 'ሐ. Color'], 'a': 'ሀ. Goal'},
        {'q': '49. የቡድን መሪ?', 'o': ['ሀ. Team Leader', 'ለ. Follower', 'ሐ. Stranger'], 'a': 'ሀ. Team Leader'},
        {'q': '50. በስራ ቦታ ደህንነት መጠበቅ?', 'o': ['ሀ. Safety Management', 'ለ. Risk Management', 'ሐ. ሁለቱም'], 'a': 'ሐ. ሁለቱም'},
    ],
    'Economics': [
        {'q': '1. ኤኮኖሚክስ ስለ ምን ያጠናል?', 'o': ['ሀ. ስለ ጤና', 'ለ. ስለ ሀብት ውስንነት', 'ሐ. ስለ ስፖርት'], 'a': 'ለ. ስለ ሀብት ውስንነት'},
        {'q': '2. ማክሮ ኤኮኖሚክስ (Macro) የሚያጠናው?', 'o': ['ሀ. ግለሰቦችን', 'ለ. ሀገራዊ ኢኮኖሚን', 'ሐ. ትናንሽ ሱቆችን'], 'a': 'ለ. ሀገራዊ ኢኮኖሚን'},
        {'q': '3. የፍላጎት (Demand) ህግ?', 'o': ['ሀ. ዋጋ ሲጨምር ፍላጎት ይቀንሳል', 'ለ. ዋጋ ሲጨምር ፍላጎት ይጨምራል', 'ሐ. ዋጋ ፍላጎትን አይቀይርም'], 'a': 'ሀ. ዋጋ ሲጨምር ፍላጎት ይቀንሳል'},
        {'q': '4. የዋጋ ግሽበት ምንድነው?', 'o': ['ሀ. Inflation', 'ለ. Deflation', 'ሐ. Stagnation'], 'a': 'ሀ. Inflation'},
        {'q': '5. GDP ማለት ምን ማለት ነው?', 'o': ['ሀ. የሀገር ውስጥ ጥቅል ምርት', 'ለ. የውጭ እርዳታ', 'ሐ. የገንዘብ ብክነት'], 'a': 'ሀ. የሀገር ውስጥ ጥቅል ምርት'},
        {'q': '6. የኢኮኖሚክስ አባት?', 'o': ['ሀ. Adam Smith', 'ለ. Karl Marx', 'ሐ. John Keynes'], 'a': 'ሀ. Adam Smith'},
        {'q': '7. "Opportunity Cost" ማለት?', 'o': ['ሀ. አማራጭን ማጣት', 'ለ. ትርፍ ማግኘት', 'ሐ. ገንዘብ መበደር'], 'a': 'ሀ. አማራጭን ማጣት'},
        {'q': '8. "Market" ምንድነው?', 'o': ['ሀ. መሸጫ ቦታ', 'ለ. ገዢና ሻጭ የሚገናኙበት', 'ሐ. ሱቅ ብቻ'], 'a': 'ለ. ገዢና ሻጭ የሚገናኙበት'},
        {'q': '9. ምርትና አገልግሎት ለገበያ ማቅረብ?', 'o': ['ሀ. Supply', 'ለ. Demand', 'ሐ. Consumption'], 'a': 'ሀ. Supply'},
        {'q': '10. "Scarcity" ምንድነው?', 'o': ['ሀ. እጥረት', 'ለ. ሙላት', 'ሐ. ስርጭት'], 'a': 'ሀ. እጥረት'},
        {'q': '11. የገንዘብ መግዛት አቅም መቀነስ?', 'o': ['ሀ. Inflation', 'ለ. Savings', 'ሐ. Growth'], 'a': 'ሀ. Inflation'},
        {'q': '12. ፍላጎትና አቅርቦት እኩል ሲሆኑ?', 'o': ['ሀ. Equilibrium', 'ለ. Surplus', 'ሐ. Shortage'], 'a': 'ሀ. Equilibrium'},
        {'q': '13. "Microeconomics" የሚያጠናው?', 'o': ['ሀ. ግለሰብና ድርጅትን', 'ለ. አለምን', 'ሐ. መንግስትን'], 'a': 'ሀ. ግለሰብና ድርጅትን'},
        {'q': '14. በነፃ ገበያ ዋጋ የሚወሰነው?', 'o': ['ሀ. በመንግስት', 'ለ. በፍላጎትና አቅርቦት', 'ሐ. በሻጭ ብቻ'], 'a': 'ለ. በፍላጎትና አቅርቦት'},
        {'q': '15. የሰው ፍላጎት?', 'o': ['ሀ. ውስን ነው', 'ለ. ገደብ የለውም', 'ሐ. የለም'], 'a': 'ለ. ገደብ የለውም'},
        {'q': '16. "Monopoly" ገበያ?', 'o': ['ሀ. አንድ ሻጭ ብቻ', 'ለ. ብዙ ሻጭ', 'ሐ. ሁለት ሻጭ'], 'a': 'ሀ. አንድ ሻጭ ብቻ'},
        {'q': '17. ታክስ (Tax) የሚሰበስበው?', 'o': ['ሀ. መንግስት', 'ለ. ባንክ', 'ሐ. ግለሰብ'], 'a': 'ሀ. መንግስት'},
        {'q': '18. የስራ አጥነት ቁጥር?', 'o': ['ሀ. Unemployment rate', 'ለ. Employment rate', 'ሐ. Interest rate'], 'a': 'ሀ. Unemployment rate'},
        {'q': '19. የወጪ ንግድ?', 'o': ['ሀ. Export', 'ለ. Import', 'ሐ. Trade'], 'a': 'ሀ. Export'},
        {'q': '20. የገቢ ንግድ?', 'o': ['ሀ. Import', 'ለ. Export', 'ሐ. Gift'], 'a': 'ሀ. Import'},
        {'q': '21. "Laissez-faire" ፍልስፍና?', 'o': ['ሀ. የመንግስት ጣልቃ ገብነት የሌለበት', 'ለ. ጥብቅ ቁጥጥር', 'ሐ. ሶሻሊዝም'], 'a': 'ሀ. የመንግስት ጣልቃ ገብነት የሌለበት'},
        {'q': '22. የትርፍ ግብ?', 'o': ['ሀ. Profit maximization', 'ለ. Loss', 'ሐ. Spending'], 'a': 'ሀ. Profit maximization'},
        {'q': '23. "Utility" ምንድነው?', 'o': ['ሀ. እርካታ', 'ለ. ስቃይ', 'ሐ. ቁጥር'], 'a': 'ሀ. እርካታ'},
        {'q': '24. የባንክ ወለድ?', 'o': ['ሀ. Interest rate', 'ለ. Exchange rate', 'ሐ. Tax rate'], 'a': 'ሀ. Interest rate'},
        {'q': '25. ካፒታሊዝም በምን ይመራል?', 'o': ['ሀ. በግል ንብረት', 'ለ. በመንግስት ንብረት', 'ሐ. በስጦታ'], 'a': 'ሀ. በግል ንብረት'},
        {'q': '26. ሶሻሊዝም የሚያተኩረው?', 'o': ['ሀ. በጋራ ንብረት', 'ለ. በሀብታም ብቻ', 'ሐ. በንግድ'], 'a': 'ሀ. በጋራ ንብረት'},
        {'q': '27. "Normal good" ምንድነው?', 'o': ['ሀ. ገቢ ሲጨምር ፍላጎቱ የሚጨምር', 'ለ. ገቢ ሲጨምር የሚቀንስ', 'ሐ. የማይፈለግ'], 'a': 'ሀ. ገቢ ሲጨምር ፍላጎቱ የሚጨምር'},
        {'q': '28. "Inferior good" ምንድነው?', 'o': ['ሀ. ገቢ ሲጨምር ፍላጎቱ የሚቀንስ', 'ለ. በጣም ውድ', 'ሐ. አልማዝ'], 'a': 'ሀ. ገቢ ሲጨምር ፍላጎቱ የሚቀንስ'},
        {'q': '29. የገበያ እጥረት (Shortage)?', 'o': ['ሀ. አቅርቦት ከፍላጎት ሲያንስ', 'ለ. አቅርቦት ሲበዛ', 'ሐ. ፍላጎት ሲጠፋ'], 'a': 'ሀ. አቅርቦት ከፍላጎት ሲያንስ'},
        {'q': '30. ትርፍ ምርት (Surplus)?', 'o': ['ሀ. አቅርቦት ከፍላጎት ሲበልጥ', 'ለ. እጥረት ሲኖር', 'ሐ. ዋጋ ሲቀንስ'], 'a': 'ሀ. አቅርቦት ከፍላጎት ሲበልጥ'},
        {'q': '31. "Oligopoly" ገበያ?', 'o': ['ሀ. ጥቂት ትልልቅ ሻጮች', 'ለ. አንድ ሻጭ', 'ሐ. ሚሊዮን ሻጭ'], 'a': 'ሀ. ጥቂት ትልልቅ ሻጮች'},
        {'q': '32. የኢኮኖሚ እድገት?', 'o': ['ሀ. Economic Growth', 'ለ. Economic Crisis', 'ሐ. Poverty'], 'a': 'ሀ. Economic Growth'},
        {'q': '33. "Human Capital" ምንድነው?', 'o': ['ሀ. የሰው እውቀትና ክህሎት', 'ለ. የሰው ቁጥር', 'ሐ. ገንዘብ'], 'a': 'ሀ. የሰው እውቀትና ክህሎት'},
        {'q': '34. ማዕከላዊ ባንክ ስራው?', 'o': ['ሀ. የገንዘብ ፖሊሲ መቆጣጠር', 'ለ. ቂጣ መጋገር', 'ሐ. ጫማ መስራት'], 'a': 'ሀ. የገንዘብ ፖሊሲ መቆጣጠር'},
        {'q': '35. "Fixed Cost" ምንድነው?', 'o': ['ሀ. የማይቀየር ወጪ', 'ለ. የሚቀያየር ወጪ', 'ሐ. ነፃ'], 'a': 'ሀ. የማይቀየር ወጪ'},
        {'q': '36. "Variable Cost" ምንድነው?', 'o': ['ሀ. እንደ ምርቱ የሚቀያየር', 'ለ. ቋሚ ወጪ', 'ሐ. ታክስ'], 'a': 'ሀ. እንደ ምርቱ የሚቀያየር'},
        {'q': '37. የፍላጎት መለጠጥ?', 'o': ['ሀ. Elasticity', 'ለ. Plasticity', 'ሐ. Hardness'], 'a': 'ሀ. Elasticity'},
        {'q': '38. "Perfect Competition"?', 'o': ['ሀ. ብዙ ገዢና ሻጭ ያለበት', 'ለ. ሻጭ የሌለበት', 'ሐ. ጦርነት'], 'a': 'ሀ. ብዙ ገዢና ሻጭ ያለበት'},
        {'q': '39. የንግድ ሚዛን (Balance of Trade)?', 'o': ['ሀ. ኤክስፖርት ሲቀነስ ኢምፖርት', 'ለ. ታክስ', 'ሐ. ብድር'], 'a': 'ሀ. ኤክስፖርት ሲቀነስ ኢምፖርት'},
        {'q': '40. "Factors of Production"?', 'o': ['ሀ. መሬት፡ ጉልበት፡ ካፒታል', 'ለ. መኪና ብቻ', 'ሐ. ምግብ'], 'a': 'ሀ. መሬት፡ ጉልበት፡ ካፒታል'},
        {'q': '41. የገንዘብ ምንዛሬ?', 'o': ['ሀ. Exchange rate', 'ለ. Birth rate', 'ሐ. Death rate'], 'a': 'ሀ. Exchange rate'},
        {'q': '42. "Deflation" ምንድነው?', 'o': ['ሀ. አጠቃላይ የዋጋ መቀነስ', 'ለ. የዋጋ መጨመር', 'ሐ. ዝምታ'], 'a': 'ሀ. አጠቃላይ የዋጋ መቀነስ'},
        {'q': '43. ድህነት?', 'o': ['ሀ. Poverty', 'ለ. Wealth', 'ሐ. Rich'], 'a': 'ሀ. Poverty'},
        {'q': '44. "Standard of Living" ጥቅሙ?', 'o': ['ሀ. የኑሮ ደረጃን ለመለካት', 'ለ. ለመጫወት', 'ሐ. ለመተኛት'], 'a': 'ሀ. የኑሮ ደረጃን ለመለካት'},
        {'q': '45. ምርታማነት?', 'o': ['ሀ. Productivity', 'ለ. Laziness', 'ሐ. Sleeping'], 'a': 'ሀ. Productivity'},
        {'q': '46. "Fiscal Policy" የሚወጣው በ?', 'o': ['ሀ. በመንግስት', 'ለ. በባንክ', 'ሐ. በቤተክርስቲያን'], 'a': 'ሀ. በመንግስት'},
        {'q': '47. "Monetary Policy" የሚወጣው በ?', 'o': ['ሀ. በማዕከላዊ ባንክ', 'ለ. በንግድ ቤት', 'ሐ. በፖሊስ'], 'a': 'ሀ. በማዕከላዊ ባንክ'},
        {'q': '48. የፍጆታ እቃዎች?', 'o': ['ሀ. Consumer goods', 'ለ. Capital goods', 'ሐ. Raw materials'], 'a': 'ሀ. Consumer goods'},
        {'q': '49. የካፒታል እቃዎች?', 'o': ['ሀ. ማሽኖችና ህንፃዎች', 'ለ. ዳቦ', 'ሐ. ልብስ'], 'a': 'ሀ. ማሽኖችና ህንፃዎች'},
        {'q': '50. አለም አቀፍ ንግድ?', 'o': ['ሀ. International Trade', 'ለ. Local Trade', 'ሐ. No Trade'], 'a': 'ሀ. International Trade'},
    ]
}

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data_store[user_id] = {'count': 0, 'score': 0}
    keyboard = [['Management', 'Economics']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👋 ሰላም! ID: {user_id}\nትምህርት ምረጥ።", reply_markup=reply_markup)

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    target_id = context.args[0]
    add_paid_user(target_id)
    await update.message.reply_text(f"✅ ID {target_id} አግብርያለሁ!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    paid_users = get_paid_users()
    if user_id not in user_data_store: user_data_store[user_id] = {'count': 0, 'score': 0}
    if user_id not in paid_users and user_data_store[user_id]['count'] >= 20:
        await update.message.reply_text(f"🛑 ነፃ ሙከራ አልቋል! ID: {user_id} ለ @papilololo ይላኩ።")
        return
    if text in EXAMS:
        context.user_data['current_exam'] = text
        await ask_random_question(update, context)
    elif 'current_exam' in context.user_data:
        last_q = context.user_data.get('last_q')
        if last_q and text in last_q['o']:
            user_data_store[user_id]['count'] += 1
            msg = "✅ ትክክል!" if text == last_q['a'] else f"❌ ተሳስተሃል! መልሱ: {last_q['a']}"
            await update.message.reply_text(f"{msg}\n📊 ተራ: {user_data_store[user_id]['count']}")
            await ask_random_question(update, context)

async def ask_random_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exam_type = context.user_data['current_exam']
    q = random.choice(EXAMS[exam_type])
    context.user_data['last_q'] = q
    reply_markup = ReplyKeyboardMarkup([q['o']], resize_keyboard=True)
    await update.message.reply_text(q['q'], reply_markup=reply_markup)

if __name__ == '__main__':
    # 1. 'ደወሉን' (Flask) ከበስተጀርባ እናስነሳው
    threading.Thread(target=run_flask).start()
    
    # 2. ቦቱን እናስነሳው (Render ላይ Proxy አያስፈልግም!)
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("activate", activate))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("ሮቦቱ ስራ ጀምሯል...")
    application.run_polling()
