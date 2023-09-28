import nsepythonserver 
import seaborn as sns
import pandas as pd
import streamlit as st
from datetime import datetime
from time import gmtime, strftime
# from IPython.display import clear_output 
import matplotlib.pyplot as plt
from pytz import timezone 
# from deta import Deta



   

if __name__=='__main__':
    
    st.title('WELCOME BULLS CARTEL')
    st.header('WELCOME TO NIFTY 50')
    today_date =strftime("%d %b %Y", gmtime()),datetime.now(timezone("Asia/Kolkata")).strftime('%I.%M %p')
#     today_date =strftime(datetime.now(timezone("Asia/Kolkata")).strftime('%d %b %Y %I.%M %p')
    st.markdown(f"as at {today_date}")
    option= st.selectbox(
    'How would you like to be contacted?',
    ('5', '10', '15')) 
    st.write('You selected:', option)
    st.markdown('Important Information')
    st.markdown(""" CALL % INCREASE MEANS MARKET GOES DOWN  
             PUT % INCREASE MEANS MARKET GOES UP
             """)  
    # while True:
       # try:
    data=nse_fno("NIFTY")
    last_prices=round(nse_quote_ltp("NIFTY"))
    print(data)
    st.markdown(last_prices)
    # break
       # except:
       #    time.sleep(1)



# final = pd.DataFrame(columns=['Diffn', 'pcr', 'cal_per','put_per','time','dirn'])

# while True:
#     dataset,final=ploting()      
#     p1=st.empty()
#     p2=st.empty()
#     p3=st.empty()
#     # p4=st.empty()
#              # % change oi put
#     p1.dataframe(dataset.style.highlight_max(['% change oi put','% change oi'],axis=0)) #Column hightlight 
#     p2.dataframe(final.style.highlight_max(['cal_per','put_per'],axis=1)) # row highlight
#     fig, ax = plt.subplots(figsize=(6, 2)) 
#     ax.plot(final['time'],final['pcr'])
#     ax.axhline(y=0, color='black', linestyle='solid') # 0 line graph
#     fig.autofmt_xdate(rotation=70)
#     p3.pyplot(fig)
#     # p4.dataframe(all_day_data)
#     time.sleep(5*60) # how to the start again code check upper condition min * sec
#     p1.empty() # then clean all data frame 
#     p2.empty()
#     p3.empty()
#     # p4.empty()
