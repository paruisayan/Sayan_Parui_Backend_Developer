#!/usr/bin/env python
# coding: utf-8

# In[1]:


#importing necessary libraries
from sqlalchemy import create_engine
import urllib
import configparser
import pandas as pd
import sqlalchemy as db
from datetime import date
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


# In[19]:


#view full output
pd.set_option('display.max_colwidth',10000)
pd.set_option('display.max_rows', 100000)


# In[2]:



config = configparser.ConfigParser()
config.read('/datadrive/EV_analytics/EV_DB/ev_db.config.ini')
config.read('/datadrive/EV_analytics/EV_DB/ev_test/ev_db.config.ini')

server=config['server']
password=config['pass']

psql_engine_tcs = create_engine('postgresql+psycopg2://readapp:%s@%s:5432/evmain' % (urllib.parse.quote_plus(password['postgres_pass_tcs']),server["postgres_tcs"]))
psql_engine_212 = create_engine('postgresql+psycopg2://ev_db_write:%s@%s:5432/ev_database' % (urllib.parse.quote_plus(password['postgres_pass']),server["postgres_212"]))
print("success")


# In[3]:


today = date.today()
print("Today date is: ", today)
month_ago = today - dt.timedelta(days=90)
print(month_ago)
print(type(month_ago.strftime('%d-%m-%Y')))


# In[5]:


q ="""select * from ocpp_logs where identifier = 'ZJ3192000103WE' and date(time) >='2021-11-25' and date(time) <= '2022-02-02' """;
print(q)
df = pd.read_sql(q, psql_engine_tcs)
print(df.head(5))


# In[13]:


q1 ="""select * from ev_charge_point where identifier = 'ZJ3192000103WE' limit 10 """;
print(q1)
df1= pd.read_sql(q1, psql_engine_tcs)
print(df1.head(5))


# In[ ]:





# In[51]:


# # reading df
# df=pd.read_csv('ocpp_logs_history_all_data.csv')
# df.head(5)


# In[14]:


# check no of tuples
df.size


# In[15]:


#check for df length
len(df)


# In[54]:





# In[55]:




# In[16]:


df1.size


# In[57]:




# DATA PRE-PROCESSING

# In[17]:


#Filter null values
df = df.dropna(how = 'all')
df.head(5)


# In[20]:


#Filter null values
df1 = df1.dropna(how = 'all')
df1.head(5)


# In[21]:


df1.columns


# In[22]:


df = df.replace('\\N', '')


# In[23]:


df1=df1.replace('\\N', '')


# In[24]:


df.columns


# In[26]:


#dropping unnecessary columns
df=df.drop(['requestuser', 'requestsource', 'requestidentifier', 'requestmessage','hour','date','month','year'], axis = 1)
df.head(5)


# In[27]:


#dropping NaN from msg column
df= df[df['msg'].notna()]
df.head(5)


# In[28]:


df1.columns


# In[30]:


#dropping unnecessary columns
df1=df1.drop(['firmwareversion', 'iccid', 'imsi',
       'metertype', 'meterserialnumber', 'time', 'model_id', 'cdmstatus',
       'devicestatus', 'latitude', 'longitude', 'address', 'address2',
       'landmark', 'postalcode', 'country',
       'locationid', 'type', 'success_rate',
       'inactivitynotificationsent', 'inactivitynotificationsenttime',
       'inactivitynotificationid', 'inactivitynotificationtype',
       'inactivitynotificationresettime', 'manageflaginventory',
       'manageflaginventorytime'], axis = 1)
df1.head(5)


# In[31]:


#renaming column name
df1.rename(columns = {'name':'Charging Station Name'}, inplace = True)
df1.head(5)


# In[32]:


df.head(5)


# In[33]:


# check for null values
df.isna().sum()


# In[34]:


df1.isna().sum()


# In[35]:


# replace null values with empty string
df1 = df1.fillna(' ')
df1.isna().sum()


# In[36]:


# replace null values with empty string
df = df.fillna(' ')
df.isna().sum()


# In[37]:


ocpp_with_location = pd.merge(df, df1, 
                   on='identifier', 
                   how='inner')
ocpp_with_location.head(5)


# In[38]:


ocpp_with_location.rename(columns = {'id_x':'id'}, inplace = True)
ocpp_with_location.head(5)


# In[39]:


ocpp_with_location=ocpp_with_location.drop(['id_y','chargepointserialnumber'],axis=1)
ocpp_with_location.head(5)


# In[41]:


ocpp_with_location.to_csv("occp_ZJ3192000103WE.csv")


# In[42]:


df= ocpp_with_location.copy()


# In[43]:


df.size


# In[44]:


len(df)


# In[45]:


# column names
df.columns


# In[46]:


# get identifier data type
df.info()


# In[47]:


#extract year, month and day for analysis
df['year'] = pd.DatetimeIndex(df['time']).year
df['month'] = pd.DatetimeIndex(df['time']).month
df['day'] = pd.DatetimeIndex(df['time']).day
df.head(5)


# In[48]:


# check for any null values
df.isna().sum()


# In[49]:


# total vendors present
df[['chargepointvendor']].value_counts()



# In[124]:





# In[126]:





# In[127]:




# In[128]:





# In[129]:




# 1. POWER SUPPLY LOSS 

# In[50]:


# adding a column= boot notification for keeping track of no of boot notifications occured
boot_notification_request_index=df[df['action'].str.contains('Boot Notification Request')].index.values
boot_notification_request_index


# In[51]:


# putting value=1 where BNR occurred
for i in range(0,len(boot_notification_request_index)):
    df.at[boot_notification_request_index[i],'boot notification request'] = 1

df.head(5)


# In[52]:


df['boot notification request'].head(5)


# In[53]:


df["boot notification request"]= df["boot notification request"].replace(np.nan,0)
df.head(5)


# In[54]:


#  adding data having BNR into separate df named df_boot
df_boot = df[df['boot notification request'] >0]
df_boot.head(5)


# In[55]:


#getting size of df_boot
len(df_boot)


# In[56]:


# total rows
print("Count of total boot notification requests ->",len(df_boot))


# In[57]:


df_boot.columns


# In[58]:


#top identifiers where boot notification occurred maximum no of times 
top_identifiers_with_BN = df_boot.groupby(['identifier']).size().reset_index().rename(columns={0: 'boot_notification_count'}).sort_values(by='boot_notification_count', ascending = False).reset_index(drop=True)
top_identifiers_with_BN.head(5)


# 2. NETWORK CONNECTION LOST/DISCONNECTED

# In[60]:


df.head(5)


# In[61]:


df['state_0'] = df['action']
df['state_1'] = df['action'].shift(-1)
df['state_2'] = df['action'].shift(-2)
df['state_3'] = df['action'].shift(-3)
df['state_4'] = df['action'].shift(-4)
df.head(5)


# In[62]:


df['SNR'] = np.where(((df['state_0'] == 'Connection Lost/Disconnected') & (df['state_1'] == 'Connection Initiated') & (df['state_2'] == 'Status Notification Request') & (df['state_3'] == 'Status Notification Request') &(df['state_4'] == 'Status Notification Request') ), 1, 0) 
print(df['SNR'].value_counts())


# In[63]:


df=df.drop(['state_0', 'state_1', 'state_2', 'state_3', 'state_4'], axis=1)
df.head(5)


# In[64]:


#  adding data having SNR into separate df named df_status
df_snr = df[df['SNR'] >0]
df_snr.head(5)


# In[65]:


# total rows
print("Count of total boot notification requests ->",len(df_snr))


# In[66]:


#top identifiers where SNR occurred maximum no of times 
top_identifiers_with_SNR = df_snr.groupby(['identifier']).size().reset_index().rename(columns={0: 'SNR_count'}).sort_values(by='SNR_count', ascending = False).reset_index(drop=True)
top_identifiers_with_SNR.head(5)


# In[80]:


boot_count= top_identifiers_with_BN['boot_notification_count']
print(boot_count)
snr_count= top_identifiers_with_SNR['SNR_count']
print(snr_count)
print("boot percentage:", boot_count/ (boot_count+ snr_count) * 100, "%")
print("snr percentage:", snr_count/ (boot_count+ snr_count) * 100, "%")

