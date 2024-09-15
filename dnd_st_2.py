
#%% LIBRARIES
import numpy as np
import pandas as pd
import requests
import streamlit as st
#import discord
import json
import os
from bs4 import BeautifulSoup as bs

st.set_page_config(
    layout="wide",
    )

#%% initialisation
select = '--- Selectionnez ---'

listInit = ['race','sousrace','classe1','sousclass1','classe2','sousclass2','historique']

for i in listInit:
    if i not in st.session_state:
        st.session_state[i] = select

if 'lvl1' not in st.session_state:
    st.session_state['lvl1'] = 1

if 'lvl2' not in st.session_state:
    st.session_state['lvl2'] = 1

if 'dons' not in st.session_state:
    st.session_state['dons'] = []
    
# if 'nom' not in st.session_state:
#     st.session_state['nom'] = ''

maxLvl=5

#%% functions

@st.cache_data
def loadDataFrame(path):
    return pd.read_csv( path, index_col = 0 )

@st.cache_data
def list_files_with_suffix(folder_path, suffix):
    """
    List all files in a folder whose names end with the given suffix.
    
    :param folder_path: Path to the folder
    :param suffix: Suffix to match the end of file names
    :return: List of file names ending with the suffix
    """
    try:
        # List all files in the folder
        files = os.listdir(folder_path)
        
        # Filter files that end with the given suffix
        #matching_files = [f for f in files if f.endswith(suffix)]
        matching_files = [f[:-len(suffix)] for f in files if f.endswith(suffix)]
        
        return matching_files
    except FileNotFoundError:
        print(f"The folder {folder_path} does not exist.")
        return []
    except PermissionError:
        print(f"Permission denied to access the folder {folder_path}.")
        return []

#%%

def ajoutTextDf( globalIndicator , title, source, sourceTxt , descri , flag = 0  ):
    
   
    
    textTemplate = [
        {'name':'repeating_traits_'+globalIndicator+'_name',        'current':title,    'max':'','id':'-'+globalIndicator+'Name'}, # name / title
        {'name':'repeating_traits_'+globalIndicator+'_source',    'current':source,   'max':'','id':'-'+globalIndicator+'Source'}, # source ~ Race / Feat / Class ...
        {'name':'repeating_traits_'+globalIndicator+'_source_type',    'current':sourceTxt,   'max':'','id':'-'+globalIndicator+'SourceType'}, # source text
        {'name':'repeating_traits_'+globalIndicator+'_options-flag', 'current':str(flag),'max':'','id':'-'+globalIndicator+'Flag'}, # flag > let it to 0
        
        {'name':'repeating_traits_'+globalIndicator+'_display_flag', 'current':"on",'max':'','id':'-'+globalIndicator+'DisplayFlag'}, # flag > let it to 0
        
        
        {'name':'repeating_traits_'+globalIndicator+'_description',    'current':descri,   'max':'','id':'-'+globalIndicator+'Descri'}, # text
        
        ]

    return pd.DataFrame( textTemplate )

#%%
def ajoutText( df, globalIndicator , title, source, sourceTxt , descri , flag = 0 ):
    
    globalIndicator = '-'+globalIndicator
    
    tmpDf = ajoutTextDf( globalIndicator , title, source,sourceTxt , descri , flag = 0  )
    
    ind = df.loc[ df['name'] == '_reporder_repeating_traits' ].index[0]
    
    #au début de la pile
    #df.at[ ind ,'current'] = globalIndicator+',' + df.at[ ind ,'current']
    
    #à la fin de la pile
    df.at[ ind ,'current'] =  df.at[ ind ,'current'] +',' + globalIndicator
    
    df = pd.concat([df,tmpDf]).reset_index(drop=True)
    
    return df

#%%


# note : tout n'est pas inclu

# info de base (nom, stats, pv , ...)
# Race
# Class 1
# Class 2 (optionnal)
# (subclass not included yet)
# Background

def buildCharacterV1( nomPerso, stats, pvs, race, subrace, class1,lvl1, class2,lvl2 , background, feats , fileName = 'newFile'):
    with open('./json/Fiche Vide.json', 'r',encoding='utf-8') as file:
        data = json.load(file)
        
    listOfDict = data['character']['attribs']

    
    dfJson = pd.DataFrame( listOfDict )
    dfJson['current'] = dfJson['current'].astype('str') 
    
    ##### INFO BASE #####
    
    # nom fiche
    data['character']['name'] = nomPerso
    

    ##### RACE #####
    dfRace = pd.read_csv( './races/'+race+'Comb.csv' )
    dfRace = dfRace[ dfRace['subrace'] == subrace ].fillna('')
    
    dfJson = ajoutText( dfJson ,  'RaceHeader' , '======= RACE =======', 'Race', subrace , '' , flag = 0 )
    dfJson = ajoutText( dfJson ,  'RaceDenom' , str.upper(subrace), 'Race', subrace , '' , flag = 0 )
    
    for idx, row in dfRace.iterrows():
        dfJson = ajoutText( dfJson ,  'Race'+str(idx) , row['section FR'], 'Race', subrace , row['content FR'] , flag = 0 )
    
    
    ##### CLASS 1 #####
    dfClass1 = pd.read_csv( './classes/' + class1+'20tableFull.csv' , index_col = 0 ).fillna('')
    #dfClass1['Level'] = [ int(i[:-2]) for i in  dfClass1['Level'] ]

    dfClass1 = dfClass1[ dfClass1['Level'] <= lvl1 ]
    #dfClass1 = dfClass1[ pd.to_numeric(dfClass1['Level'],errors='coerce') <= lvl1 ]
    #dfClass1 = dfClass1[ dfClass1['Level'].astype('int') <= lvl1 ]
    
    dfJson = ajoutText( dfJson ,  'Class1Header' , '======= CLASSE 1 =======', 'Class', class1 , '' , flag = 0 )
    dfJson = ajoutText( dfJson ,  'Class1Denom' , str.upper(class1), 'Class', class1 , '' , flag = 0 )
    
    for idx, row in dfClass1.iterrows():
        dfJson = ajoutText( dfJson ,  'Class1-'+str(idx) , row['Capacites'], 'Class', class1 + ' niv .' + str(row['Level']) , row['Capacites Texts'] , flag = 0 )
    
    
    ##### CLASS 2 #####
    if( class2 ):
        dfClass2 = pd.read_csv( './classes/' + class2+'20tableFull.csv' , index_col = 0 ).fillna('')
        #dfClass2['Level'] = [ int(i[:-2]) for i in  dfClass2['Level'] ]

        dfClass2 = dfClass2[ dfClass2['Level'] <= lvl2 ]   
        
        dfJson = ajoutText( dfJson ,  'Class2Header' , '======= CLASSE 2 =======', 'Class', class2 , '' , flag = 0 )
        dfJson = ajoutText( dfJson ,  'Class2Denom' , str.upper(class2), 'Class', class2 , '' , flag = 0 )
        
        for idx, row in dfClass2.iterrows():
            dfJson = ajoutText( dfJson ,  'Class2-'+str(idx) , row['Capacites'], 'Class', class2 + ' niv .' + str(row['Level']) , row['Capacites Texts'] , flag = 0 )
        
    
    ##### BACKGROUND #####
    dfBG = pd.read_csv( './backgrounds/dfBackground.csv', index_col = 0 ).fillna('')
    rowBG = dfBG[ dfBG['background'].str.lower() == background ].iloc[0]

    dfJson = ajoutText( dfJson ,  'HistoHeader' , '===== HISTORIQUE =====', 'Background', background , '' , flag = 0 )
    dfJson = ajoutText( dfJson ,  'HistoDenom' , str.upper(background), 'Background', background , '' , flag = 0 )
    
    # description de l'historique
    dfJson = ajoutText( dfJson ,  'HistoDescri' , 'Description', 'Background', background , rowBG['description FR'] , flag = 0 )
    # equipement
    dfJson = ajoutText( dfJson ,  'HistoEqpmt' , 'Equipement', 'Background', background , rowBG['equipement text FR'] , flag = 0 )
    # maitrise
    dfJson = ajoutText( dfJson ,  'HistoSkills' , 'Maitrises', 'Background', background , ' , '.join(eval(rowBG['skills'])) , flag = 0 )
    # languages
    dfJson = ajoutText( dfJson ,  'HistoLangue' , 'Langues', 'Background', background , rowBG['languages FR'] , flag = 0 )
    # outils
    dfJson = ajoutText( dfJson ,  'HistoTool' , 'Outils', 'Background', background , rowBG['tools FR'] , flag = 0 )
    
    
    ### FEATS
    dfFeat = pd.read_csv('./Feats/featTable.csv',index_col=0).fillna('')
    dfJson = ajoutText( dfJson ,  'FeatHeader' , '===== DONS/FEATS =====', 'Feat', '' , '' , flag = 0 )
  
    
    for f in feats:
        serieFeatTmp = dfFeat[ dfFeat['Feat'] == f ].iloc[0]
        
        #ajout
        dfJson = ajoutText( dfJson ,  f+'Denom' , str.upper(serieFeatTmp['Dons']), 'Feat',
                           serieFeatTmp['Dons']+' | '+serieFeatTmp['Feat'],
                            serieFeatTmp['Descri. Fr'] , flag = 0 )
        
    
    
    #####
    # INPUT DATA TO JSON AND SAAVE FILE
    #####

    data['character']['attribs'] = dfJson.to_dict('records')
    
    return data
    
    # if(nomPerso):
    #     out_file = open("./json/"+nomPerso+".json", "w")
    # else:
    #     out_file = open("./json/"+'newFile'+".json", "w")

    # json.dump(data, out_file, indent = 4)

    # out_file.close()


#%% welcome and information
st.title('LE CONSTRUCTEUR DE FICHE DE PERSONNAGE DES ARCHES PROTOTYYPE V0.1')
st.write('ceci est un prototype. pour le moment il s agit de collecter (et d afficher) les different information necessaire à la constructoin dun personnage')
st.write('certaines choses devront dans tous les cas etre faites à la main, ou hard coded')
st.write('ce code ne comprend pas tout et reste un prototype')
st.write('des problèmes peuvent subister dans les données fournie, et il ny a pas de garantie que tout soit autoriser sur le serveur actuellement')

#%%

# nom du personnage
st.text_input("nom perso", "Nom du personnage",key='nom')
            
#st.write(st.session_state.nom )     

#%% Races

listRace = list_files_with_suffix(folder_path='./races/', suffix='Comb.csv')

st.selectbox(
        "Quelle est votre Race ? ",
        [select]+listRace,
        key='race'
    )

#%%


if( st.session_state.race != select ):
    dfRace = loadDataFrame('./races/'+st.session_state.race+'Comb.csv')

    st.selectbox(
            "Quelle est votre Sous Race ? ",
            [select]+list(dfRace['subrace'].unique()),
            key='sousrace'
        )

if( st.session_state.sousrace != select ):
    dfSousRace = loadDataFrame('./races/'+st.session_state.race+'Comb.csv')
    dfSousRace = dfSousRace[dfSousRace['subrace']==st.session_state.sousrace]
    
#%% Classe 1
listClass = [
    "Barbarian",
    "Bard",
    "Cleric",
    "Druid",
    "Fighter",
    "Monk",
    "Paladin",
    "Ranger",
    "Rogue",
    "Sorcerer",
    "Warlock",
    "Wizard",
    "Artificer"
]

dictEnFrClass = {
    "Barbarian":'Barbare',
    "Bard":'Barde',
    "Cleric":'Pretre',
    "Druid":'Druide',
    "Fighter":'Guerrier',
    "Monk":'Moine',
    "Paladin":'Paladin',
    "Ranger":'Rodeur',
    "Rogue":'Roublard',
    "Sorcerer":'Sorcier',
    "Warlock":'Occultiste',
    "Wizard":'Magicien',
    "Artificer":'Artificier'
 }

listEnFrClass = [ i[1] + ' | '+ i[0] for i in dictEnFrClass.items() ]

cl1, cl2 = st.columns(2)

with cl1:
    st.selectbox(
        "Quelle est votre classe primaire ? ",
        [select]+listEnFrClass,
        key='classe1'
    )
    
    if( st.session_state.classe1 != select ):
        idx_c1 =  listEnFrClass.index( st.session_state['classe1'] )
        
        dfClasse1 = loadDataFrame('./classes/'+listClass[idx_c1]+'20tableFull.csv')

        #st.write(dfClasse1)
        
        st.number_input('Niveau de votre classe primaire', 
                        min_value=1, max_value=maxLvl, 
                        value=st.session_state['lvl1'], step=1, 
                        format=None, 
                        key='lvl1',)

#%% clss 2 tmp


with cl2:
    st.selectbox(
        "Quelle est votre classe secondaire ? ",
        [select]+listEnFrClass,
        key='classe2'
    )
    
    if( st.session_state.classe2 != select ):
        idx_c2 =  listEnFrClass.index( st.session_state['classe2'] )
        
        dfClasse2 = loadDataFrame('./classes/'+listClass[idx_c2]+'20tableFull.csv')

        #st.write(dfClasse2)
        
        st.number_input('Niveau de votre classe secondaire', 
                        min_value=1, max_value=maxLvl, 
                        value=st.session_state['lvl2'], step=1, 
                        format=None, 
                        key='lvl2',)

#%% historique

dfBG = loadDataFrame('./backgrounds/dfBackground.csv')

# listBG_EnFr = [ row['background FR'] + ' | '+ row['background'] + ' ' + row['skills'] for idx,row in dfBG.iterrows() ]

listBG_EnFr = []

for idx, row in dfBG.iterrows():
    listBG_EnFr.append(row['background FR'] + ' | '+ row['background'] + ' ' + row['skills'])

st.selectbox(
    "Quelle est votre historique ? ",
    [select]+listBG_EnFr,
    key='historique'
    )

#%% Dons

dfFeat = loadDataFrame('./Feats/featTable.csv')

listFeat_EnFr = []

for idx, row in dfFeat.iterrows():
    listFeat_EnFr.append(row['Dons'] + ' | '+ row['Feat'])


st.multiselect(
    "Quelle sont vos dons ? ",
    listFeat_EnFr,
    key='dons'
    )

#%% button 


select = '--- Selectionnez ---'

listInit = ['race','sousrace','classe1','sousclass1','classe2','sousclass2','historique']

for i in listInit:
    if i not in st.session_state:
        st.session_state[i] = select

if 'lvl1' not in st.session_state:
    st.session_state['lvl1'] = 1

if 'lvl2' not in st.session_state:
    st.session_state['lvl2'] = 1

if 'dons' not in st.session_state:
    st.session_state['dons'] = []

allInfo = True
allInfo = (st.session_state['race']!=select)  
allInfo = allInfo and (st.session_state['sousrace']!=select)  
allInfo = allInfo and (st.session_state['classe1']!=select) 
#allInfo = allInfo and (st.session_state['sousclass1']!=select) 
allInfo = allInfo and (st.session_state['classe2']!=select)  
#allInfo = allInfo and (st.session_state['sousclass2']!=select)  
allInfo = allInfo and (st.session_state['historique']!=select) 
allInfo = allInfo and ( st.session_state['lvl1'] + st.session_state['lvl2']*(st.session_state['classe2']!=select) == maxLvl ) 

#st.write(allInfo)

buttonActiv = st.button('Il y a toutes les informations (minimales) necessaire pour creer votre fiche ! \n Pressez ce bouton, puis cliquer sur **telecharger** un fois que votre fiche est prete', 
          key=None, disabled = not allInfo )

if(buttonActiv):
    st.write('BINGO')
    
    if(st.session_state['classe2']==select):
        st.session_state['classe2']=''
        
    # st.write(st.session_state['nom'])
    # st.write(st.session_state['race'])
    # st.write(st.session_state['sousrace'])
    # st.write(st.session_state['classe1'],'>>>',st.session_state['classe1'].split()[-1])
    # st.write(st.session_state['classe2'],'>>>',st.session_state['classe2'].split()[-1])
    # st.write(st.session_state['lvl1'])
    # st.write(st.session_state['lvl1'])
    st.write(st.session_state['historique'],'>>>',dfBG.iloc[ listBG_EnFr.index(st.session_state['historique']) ]['background'])
    
    listDonsInput = []
    
    for i in st.session_state['dons']:
        listDonsInput.append( dfFeat.iloc[listFeat_EnFr.index(i)]['Feat'] )
    
    # st.write(st.session_state['dons'],'>>>', [ i.split()[-1] for i in st.session_state['dons'] ] )
    
    data = buildCharacterV1( nomPerso=st.session_state['nom'], 
                            stats=[], pvs=[], 
                            race=st.session_state['race'], subrace=st.session_state['sousrace'], 
                            class1=st.session_state['classe1'].split()[-1], lvl1=int(st.session_state['lvl1']),
                            class2=st.session_state['classe2'].split()[-1], lvl2=int(st.session_state['lvl2']),
                            background=str.lower(dfBG.iloc[ listBG_EnFr.index(st.session_state['historique']) ]['background']) , 
                            feats = listDonsInput ,
                            fileName = 'newFile')
    
    json_string = json.dumps(data)

    st.json(json_string, expanded=True)

    st.download_button(
        label="Download JSON",
        file_name=st.session_state['nom']+".json",
        mime="application/json",
        data=json_string,
    )

    st.write('finito')

#%% download part

# json_string = json.dumps(data)

# st.json(json_string, expanded=True)

# st.download_button(
#     label="Download JSON",
#     file_name="data.json",
#     mime="application/json",
#     data=json_string,
# )
