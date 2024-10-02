
# %% LIBRARIES
import pandas as pd
import streamlit as st
import json
import os

st.set_page_config(
    layout="wide",
)

# %% initialisation
select = '--- Selectionnez ---'

listInitSelect = ['race', 'sousrace', 'classe1',
            'sousClass1', 'classe2', 'sousClass2', 'historique']

for i in listInitSelect:
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

listInitString = ['character_appearance','character_backstory','allies_and_organization',
                  'ideals','bonds','flaws','alignment','discordPV']
for i in listInitString:
    if i not in st.session_state:
        st.session_state[i] = ''

pvInit = ['pv1','pv2','pv3','pv4',]

for i in pvInit:
    if i not in st.session_state:
        st.session_state[i] = 1

lsStats = ['FOR', 'DEX', 'CON', 'INT', 'SAG', 'CHA']

for i in lsStats:
    if i not in st.session_state:
        st.session_state[i] = 10

maxLvl = 5

# %% functions


@st.cache_data
def loadDataFrame(path):
    return pd.read_csv(path, index_col=0)


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
        # matching_files = [f for f in files if f.endswith(suffix)]
        matching_files = [f[:-len(suffix)]
                          for f in files if f.endswith(suffix)]

        return matching_files
    except FileNotFoundError:
        print(f"The folder {folder_path} does not exist.")
        return []
    except PermissionError:
        print(f"Permission denied to access the folder {folder_path}.")
        return []

# %%


def ajoutTextDf(globalIndicator, title, source, sourceTxt, descri, flag=0):

    textTemplate = [
        {'name': 'repeating_traits_'+globalIndicator+'_name',        'current': title,
            'max': '', 'id': '-'+globalIndicator+'Name'},  # name / title
        # source ~ Race / Feat / Class ...
        {'name': 'repeating_traits_'+globalIndicator+'_source',
            'current': source,   'max': '', 'id': '-'+globalIndicator+'Source'},
        {'name': 'repeating_traits_'+globalIndicator+'_source_type',    'current': sourceTxt,
            'max': '', 'id': '-'+globalIndicator+'SourceType'},  # source text
        {'name': 'repeating_traits_'+globalIndicator+'_options-flag', 'current': str(
            flag), 'max': '', 'id': '-'+globalIndicator+'Flag'},  # flag > let it to 0

        {'name': 'repeating_traits_'+globalIndicator+'_display_flag', 'current': "on",
            'max': '', 'id': '-'+globalIndicator+'DisplayFlag'},  # flag > let it to 0


        {'name': 'repeating_traits_'+globalIndicator+'_description',
            'current': descri,   'max': '', 'id': '-'+globalIndicator+'Descri'},  # text

    ]

    return pd.DataFrame(textTemplate)

# %%


def ajoutText(df, globalIndicator, title, source, sourceTxt, descri, flag=0):

    globalIndicator = '-'+globalIndicator

    tmpDf = ajoutTextDf(globalIndicator, title, source,
                        sourceTxt, descri, flag=0)

    ind = df.loc[df['name'] == '_reporder_repeating_traits'].index[0]

    # au début de la pile
    # df.at[ ind ,'current'] = globalIndicator+',' + df.at[ ind ,'current']

    # à la fin de la pile
    df.at[ind, 'current'] = df.at[ind, 'current'] + ',' + globalIndicator

    df = pd.concat([df, tmpDf]).reset_index(drop=True)

    return df

# %%


def jsonVariable(df, col1, col2, value_to_match, replacement_value):
    # Check if there are any rows where col1 matches the value_to_match
    mask = df[col1] == value_to_match
    if mask.any():
        # If a match is found, replace the values in col2 for the matching rows
        df.loc[mask, col2] = replacement_value
    else:
        # If no match is found, add a new row with the value_to_match in col1 and replacement_value in col2
        df.loc[len(df)] = {col1: value_to_match, col2: replacement_value}

    # Return the modified DataFrame
    return df

# %%


if 'allInfo' not in st.session_state:
    st.session_state['allInfo'] = False


def enoughInfo():

    # allInfo = True
    allInfo = (st.session_state['race'] != select)
    # allInfo = allInfo and (st.session_state['sousrace']!=select)
    allInfo = allInfo and (st.session_state['classe1'] != select)
    # allInfo = allInfo and (st.session_state['sousclass1']!=select)
    # allInfo = allInfo and (st.session_state['classe2']!=select)
    # allInfo = allInfo and (st.session_state['sousclass2']!=select)
    allInfo = allInfo and (st.session_state['historique'] != select)
    allInfo = allInfo and (st.session_state['lvl1'] + st.session_state['lvl2']*(
        st.session_state['classe2'] != select) == maxLvl)

    st.session_state['allInfo'] = allInfo
# %%


def combine_columns_to_list(df, col1, col2):
    def combine(row):
        word1 = row[col1].lower()
        word2 = row[col2].lower()

        # Check if word1 appears in word2
        if word1 in word2:
            return word2  # Return just word2 if word1 is already in it
        else:
            # Combine both words, separating by a space
            return f"{word1} {word2}"

    # Apply the combine function to each row and return the result as a list

    return list(set(df.apply(combine, axis=1).tolist()))

# %%

# note : tout n'est pas inclu

# info de base (nom, stats, pv , ...)
# Race
# Class 1
# Class 2 (optionnal)
# (subclass not included yet)
# Background

# def buildCharacterV1( nomPerso, stats, pvs, race, subrace, class1,lvl1, class2,lvl2 , background, feats , fileName = 'newFile'):


def buildCharacterV1(nomPerso, stats, pvs, race, class1, lvl1, class2, lvl2, background, feats, fileName='newFile'):
    with open('./json/Fiche Vide.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    listOfDict = data['character']['attribs']

    dfJson = pd.DataFrame(listOfDict)
    dfJson['current'] = dfJson['current'].astype('str')

    ##### INFO BASE #####

    # nom fiche
    data['character']['name'] = nomPerso

    ##### RACE #####
    dfRace = pd.read_csv('./races/allRaces.csv')
    # dfRace = pd.read_csv( './races/'+race+'Comb.csv' )
    dfRace = dfRace[dfRace['subrace'] == race].fillna('')
    dfRace['subrace'] = dfRace['subrace'].str.lower()

    dfJson = ajoutText(dfJson,  'RaceHeader',
                       '======= RACE =======', 'Race', race, '', flag=0)
    # dfJson = ajoutText( dfJson ,  'RaceDenom' , str.upper(subrace), 'Race', subrace , '' , flag = 0 )

    for idx, row in dfRace.iterrows():
        dfJson = ajoutText(dfJson,  'Race'+str(idx),
                           row['section FR'], 'Race', race, row['content FR'], flag=0)

    dfJson = jsonVariable(dfJson, 'name', 'current', 'race', race)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'race_display', race)

    ##### BACKGROUND #####
    dfBG = pd.read_csv('./backgrounds/dfBackground.csv',
                       index_col=0).fillna('')
    rowBG = dfBG[dfBG['background'].str.lower() == background].iloc[0]

    dfJson = ajoutText(dfJson,  'HistoHeader', '===== HISTORIQUE =====',
                       'Background', background, '', flag=0)
    # dfJson = ajoutText( dfJson ,  'HistoDenom' , str.upper(background), 'Background', background , '' , flag = 0 )

    # description de l'historique
    dfJson = ajoutText(dfJson,  'HistoDescri', 'Description',
                       'Background', background, rowBG['description FR'], flag=0)
    # equipement
    dfJson = ajoutText(dfJson,  'HistoEqpmt', 'Equipement',
                       'Background', background, rowBG['equipement text FR'], flag=0)
    # maitrise
    dfJson = ajoutText(dfJson,  'HistoSkills', 'Maitrises', 'Background',
                       background, ' , '.join(eval(rowBG['skills'])), flag=0)
    # languages
    dfJson = ajoutText(dfJson,  'HistoLangue', 'Langues',
                       'Background', background, rowBG['languages FR'], flag=0)
    # outils
    dfJson = ajoutText(dfJson,  'HistoTool', 'Outils',
                       'Background', background, rowBG['tools FR'], flag=0)

    ##### CLASS 1 #####
    classDisplay = class1 + ' ' + str(lvl1)

    dfJson = jsonVariable(dfJson, 'name', 'current', 'class', class1)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'base_level', lvl1)

    dfClass1 = pd.read_csv('./classes/' + class1 +
                           '20tableFull.csv', index_col=0).fillna('')
    # dfClass1['Level'] = [ int(i[:-2]) for i in  dfClass1['Level'] ]

    dfClass1 = dfClass1[dfClass1['Level'] <= lvl1]
    # dfClass1 = dfClass1[ pd.to_numeric(dfClass1['Level'],errors='coerce') <= lvl1 ]
    # dfClass1 = dfClass1[ dfClass1['Level'].astype('int') <= lvl1 ]

    dfJson = ajoutText(dfJson,  'Class1Header',
                       '======= CLASSE 1 =======', 'Class', class1, '', flag=0)
    # dfJson = ajoutText( dfJson ,  'Class1Denom' , str.upper(class1), 'Class', class1 , '' , flag = 0 )

    for idx, row in dfClass1.iterrows():
        dfJson = ajoutText(dfJson,  'Class1-'+str(idx), row['Capacites'], 'Class', class1 + ' niv .' + str(
            row['Level']), row['Capacites Texts'], flag=0)

    ##### CLASS 2 #####
    if (class2):
        classDisplay += ' , ' + class2 + ' ' + str(lvl2)

        dfJson = jsonVariable(dfJson, 'name', 'current',
                              'multiclass1_flag', 1)
        dfJson = jsonVariable(dfJson, 'name', 'current', 'multiclass1', class2)
        dfJson = jsonVariable(dfJson, 'name', 'current',
                              'multiclass1_lvl', lvl2)

        dfClass2 = pd.read_csv('./classes/' + class2 +
                               '20tableFull.csv', index_col=0).fillna('')
        # dfClass2['Level'] = [ int(i[:-2]) for i in  dfClass2['Level'] ]

        dfClass2 = dfClass2[dfClass2['Level'] <= lvl2]

        dfJson = ajoutText(dfJson,  'Class2Header',
                           '======= CLASSE 2 =======', 'Class', class2, '', flag=0)
        # dfJson = ajoutText( dfJson ,  'Class2Denom' , str.upper(class2), 'Class', class2 , '' , flag = 0 )

        for idx, row in dfClass2.iterrows():
            dfJson = ajoutText(dfJson,  'Class2-'+str(idx), row['Capacites'], 'Class', class2 + ' niv .' + str(
                row['Level']), row['Capacites Texts'], flag=0)

    dfJson = jsonVariable(dfJson, 'name', 'current',
                          'class_display', classDisplay)

    # FEATS
    dfFeat = pd.read_csv('./feats/featTable.csv', index_col=0).fillna('')
    dfJson = ajoutText(dfJson,  'FeatHeader',
                       '===== DONS/FEATS =====', 'Feat', '', '', flag=0)

    for f in feats:
        serieFeatTmp = dfFeat[dfFeat['Feat'] == f].iloc[0]

        # ajout
        dfJson = ajoutText(dfJson,  f+'Denom', str.upper(serieFeatTmp['Dons']), 'Feat',
                           serieFeatTmp['Dons']+' | '+serieFeatTmp['Feat'],
                           serieFeatTmp['Descri. Fr'], flag=0)

    #####
    # INPUT DATA TO JSON AND SAVE FILE
    #####
    dfJson = dfJson.fillna('') # necessaryy to avoid problem
    data['character']['attribs'] = dfJson.to_dict('records')

    return data
#%% VVVVVVV2222222222222222

# structure de stats :
    
# stats = {
#        strength :  {flat: 10, race:2,feat:1}
#     }

def buildCharacterV2(nomPerso, stats, discStats, pvs, discPvs, race, class1, sc1, lvl1, class2, sc2, lvl2, background, feats,
                     character_appearance,character_backstory,allies_and_organization,ideals,bonds,flaws,Alignment,
                     fileName='newFile'):
    with open('./json/Fiche Tres Vide.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    listOfDict = data['character']['attribs']

    dfJson = pd.DataFrame(listOfDict)
    dfJson['current'] = dfJson['current'].astype('str')

    ##### INFO BASE #####

    # nom fiche
    data['character']['name'] = nomPerso
    
    
    ### STATs
    textStat =  'Force '+ str(stats['strength']['flat'])+ ' + ' + str(stats['strength']['race']) + ' + ' + str(stats['strength']['feat']) + ' = ' + str(sum(stats['strength'].values())) + '\n' + \
                'Dextérité '+ str(stats['dexterity']['flat'])+ ' + ' + str(stats['dexterity']['race']) + ' + ' + str(stats['dexterity']['feat']) + ' = ' + str(sum(stats['dexterity'].values())) + '\n' + \
                'Constitution '+ str(stats['constitution']['flat'])+ ' + ' + str(stats['constitution']['race']) + ' + ' + str(stats['constitution']['feat']) + ' = ' + str(sum(stats['constitution'].values())) + '\n' + \
                'Intelligence '+ str(stats['intelligence']['flat'])+ ' + ' + str(stats['intelligence']['race']) + ' + ' + str(stats['intelligence']['feat']) + ' = ' + str(sum(stats['intelligence'].values())) + '\n' + \
                'Sagesse '+ str(stats['wisdom']['flat'])+ ' + ' + str(stats['wisdom']['race']) + ' + ' + str(stats['wisdom']['feat']) + ' = ' + str(sum(stats['wisdom'].values())) + '\n' + \
                'Charisme '+ str(stats['charisma']['flat'])+ ' + ' + str(stats['charisma']['race']) + ' + ' + str(stats['charisma']['feat']) + ' = ' + str(sum(stats['charisma'].values())) + '\n' 
    
    textStat += '\n'+discStats+'\n'

    dfJson = ajoutText(dfJson,  'Stats',
                       'Stats', 'Autre', '', textStat, flag=0)
    
    
    
    ## implent stats
    for s in ['strength','dexterity','constitution','intelligence','charisma','wisdom']:
        dfJson = jsonVariable(dfJson, 'name', 'current', s+'_base', stats[s]['flat'])
        dfJson = jsonVariable(dfJson, 'name', 'current', s, sum(stats[s].values()))
        dfJson = jsonVariable(dfJson, 'name', 'current', s+'_mod', (sum(stats[s].values())-10)//2)
    
    ### PVs
    textPv = ''
    conModif = (sum(stats['constitution'].values())-10)//2
    
    for x,pv in enumerate(pvs):
        textPv+= 'Lvl '+str(x)+' : '+str(pv)+' + '+str(conModif)+' + Feat/.race'+'\n'
    
    textPv += '\n'+discPvs+'\n'
    
    dfJson = ajoutText(dfJson,  'PVsStats',
                       'Les PVs (cest la vie)', 'Autre', '', textPv, flag=0)
   
    # adjust hp in sheet
    totPV = sum(pvs) + len(pvs)*conModif
    dfJson = jsonVariable(dfJson, 'name', 'current', 'hp', str(totPV))
    ### Google Sheet
    
    dfJson = ajoutText(dfJson,  'GGsheet',
                       'Google Sheet (Suivi)', 'Autre', '', 'Template: docs.google.com/spreadsheets/d/1Dr3aJ_WjY9AU8-MBc3W9EofBgW22TewS32b7BaIZm3g/edit?usp=sharing', flag=0)

    ##### RACE #####
    dfRace = pd.read_csv('./races/allRaces.csv')
    # dfRace = pd.read_csv( './races/'+race+'Comb.csv' )
    dfRace = dfRace[dfRace['subrace'] == race].fillna('')
    dfRace['subrace'] = dfRace['subrace'].str.lower()

    dfJson = ajoutText(dfJson,  'RaceHeader',
                       '======= RACE =======', 'Race', race, '', flag=0)
    # dfJson = ajoutText( dfJson ,  'RaceDenom' , str.upper(subrace), 'Race', subrace , '' , flag = 0 )

    for idx, row in dfRace.iterrows():
        dfJson = ajoutText(dfJson,  'Race'+str(idx),
                           row['section FR'], 'Race', race, row['content FR'], flag=0)

    dfJson = jsonVariable(dfJson, 'name', 'current', 'race', race)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'race_display', race)

    ##### BACKGROUND #####
    dfBG = pd.read_csv('./backgrounds/dfBackground.csv',
                       index_col=0).fillna('')
    rowBG = dfBG[dfBG['background'].str.lower() == background].iloc[0]

    dfJson = ajoutText(dfJson,  'HistoHeader', '===== HISTORIQUE =====',
                       'Background', background, '', flag=0)
    # dfJson = ajoutText( dfJson ,  'HistoDenom' , str.upper(background), 'Background', background , '' , flag = 0 )

    # description de l'historique
    dfJson = ajoutText(dfJson,  'HistoDescri', 'Description',
                       'Background', background, rowBG['description FR'], flag=0)
    # equipement
    dfJson = ajoutText(dfJson,  'HistoEqpmt', 'Equipement',
                       'Background', background, rowBG['equipement text FR'], flag=0)
    # maitrise
    dfJson = ajoutText(dfJson,  'HistoSkills', 'Maitrises', 'Background',
                       background, ' , '.join(eval(rowBG['skills'])), flag=0)
    # languages
    dfJson = ajoutText(dfJson,  'HistoLangue', 'Langues',
                       'Background', background, rowBG['languages FR'], flag=0)
    # outils
    dfJson = ajoutText(dfJson,  'HistoTool', 'Outils',
                       'Background', background, rowBG['tools FR'], flag=0)

    ##### CLASS 1 #####
    classDisplay = class1 + ' ' + str(lvl1)

    dfJson = jsonVariable(dfJson, 'name', 'current', 'class', class1)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'base_level', lvl1)

    dfClass1 = pd.read_csv('./classes/' + class1 +
                           '20tableFull.csv', index_col=0).fillna('')
    # dfClass1['Level'] = [ int(i[:-2]) for i in  dfClass1['Level'] ]

    dfClass1 = dfClass1[dfClass1['Level'] <= lvl1]
    # dfClass1 = dfClass1[ pd.to_numeric(dfClass1['Level'],errors='coerce') <= lvl1 ]
    # dfClass1 = dfClass1[ dfClass1['Level'].astype('int') <= lvl1 ]

    dfJson = ajoutText(dfJson,  'Class1Header',
                       '======= CLASSE 1 =======', 'Class', class1, '', flag=0)
    # dfJson = ajoutText( dfJson ,  'Class1Denom' , str.upper(class1), 'Class', class1 , '' , flag = 0 )

    for idx, row in dfClass1.iterrows():
        dfJson = ajoutText(dfJson,  'Class1-'+str(idx), row['Capacites'], 'Class', class1 + ' niv .' + str(
            row['Level']), row['Capacites Texts'], flag=0)
    
    ##### SOUS CLASS 1 #####
    dfSC1 = pd.read_csv('./subclasses/' + str.lower(class1) +
                           'Sc.csv', index_col=0).fillna('')
    
    dfSC1 = dfSC1[ dfSC1['subclass']==sc1 ] # selcet the subclaass
    dfSC1 = dfSC1[ dfSC1['levels']<=lvl1 ] # filter feature availale at this level
    
    dfJson = ajoutText(dfJson,  'SClass1Header',
                       '===== SOUS CLASSE 1 =====', 'Class', sc1, '', flag=0)
    for idx, row in dfSC1.iterrows():
        dfJson = ajoutText(dfJson,  'SClass1-'+str(idx), row['contability_FR'], 'Class', sc1 + ' niv .' + str(
            row['levels']), row['content_FR'], flag=0)
    
    
    ##### CLASS 2 #####
    if (class2):
        classDisplay += ' , ' + class2 + ' ' + str(lvl2)

        dfJson = jsonVariable(dfJson, 'name', 'current',
                              'multiclass1_flag', '1')
        dfJson = jsonVariable(dfJson, 'name', 'current', 'multiclass1', class2)
        dfJson = jsonVariable(dfJson, 'name', 'current',
                              'multiclass1_lvl', lvl2)

        dfClass2 = pd.read_csv('./classes/' + class2 +
                               '20tableFull.csv', index_col=0).fillna('')
        # dfClass2['Level'] = [ int(i[:-2]) for i in  dfClass2['Level'] ]

        dfClass2 = dfClass2[dfClass2['Level'] <= lvl2]

        dfJson = ajoutText(dfJson,  'Class2Header',
                           '======= CLASSE 2 =======', 'Class', class2, '', flag=0)
        # dfJson = ajoutText( dfJson ,  'Class2Denom' , str.upper(class2), 'Class', class2 , '' , flag = 0 )

        for idx, row in dfClass2.iterrows():
            dfJson = ajoutText(dfJson,  'Class2-'+str(idx), row['Capacites'], 'Class', class2 + ' niv .' + str(
                row['Level']), row['Capacites Texts'], flag=0)
            
            
        ##### SOUS CLASS 2 #####
        dfSC2 = pd.read_csv('./subclasses/' + str.lower(class2) +
                               'Sc.csv', index_col=0).fillna('')
        
        dfSC2 = dfSC2[ dfSC2['subclass']==sc2 ] # selcet the subclaass
        dfSC2 = dfSC2[ dfSC2['levels']<=lvl2 ] # filter feature availale at this level
        
        dfJson = ajoutText(dfJson,  'SClass2Header',
                           '===== SOUS CLASSE 2 =====', 'Class', sc2, '', flag=0)
        for idx, row in dfSC2.iterrows():
            dfJson = ajoutText(dfJson,  'SClass2-'+str(idx), row['contability_FR'], 'Class', sc2 + ' niv .' + str(
                row['levels']), row['content_FR'], flag=0)
            
            
    dfJson = jsonVariable(dfJson, 'name', 'current',
                          'class_display', classDisplay)

    # FEATS
    dfFeat = pd.read_csv('./feats/featTable.csv', index_col=0).fillna('')
    dfJson = ajoutText(dfJson,  'FeatHeader',
                       '===== DONS/FEATS =====', 'Feat', '', '', flag=0)

    for f in feats:
        serieFeatTmp = dfFeat[dfFeat['Feat'] == f].iloc[0]

        # ajout
        dfJson = ajoutText(dfJson,  f+'Denom', str.upper(serieFeatTmp['Dons']), 'Feat',
                           serieFeatTmp['Dons']+' | '+serieFeatTmp['Feat'],
                           serieFeatTmp['Descri. Fr'], flag=0)
    #### NEW PART
    
    # character_appearance,character_backstory,allies_and_organization,ideals,bonds,flaws,Alignment
    dfJson = jsonVariable(dfJson, 'name', 'current', 'character_appearance', character_appearance)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'allies_and_organization', allies_and_organization)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'ideals', ideals)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'bonds', bonds)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'flaws', flaws)
    dfJson = jsonVariable(dfJson, 'name', 'current', 'alignment', Alignment)
    
    #####
    # INPUT DATA TO JSON AND SAVE FILE
    #####
    dfJson = dfJson.fillna('') # necessaryy to avoid problem
    data['character']['attribs'] = dfJson.to_dict('records')

    return data

# %% welcome and information
st.title('LE CONSTRUCTEUR DE FICHE DE PERSONNAGE DES ARCHES PROTOTYYPE V1.1 :dragon: :fox_face: ')
st.write('ceci est un prototype. pour le moment il s agit de collecter (et dafficher) les different information necessaire à la constructoin dun personnage')
st.write('certaines choses devront dans tous les cas être faites à la main, ou hard coded')
st.write('cette app ne comprend pas tout et reste un prototype')
st.write('des problèmes peuvent subister dans les données fournies, et il ny a pas de garantie que tout soit autorisé sur le serveur actuellement')

# %%

# nom du personnage
st.text_input("nom perso", "Nom du personnage",
              key='nom', on_change=enoughInfo)

# st.write(st.session_state.nom )

# %% Races

# listRace = list_files_with_suffix(folder_path='./races/', suffix='Comb.csv')

listRace = ['Aarakocra MPMM', 'Protector', 'Scourge',
            'Fallen', 'Aasimar MPMM',
            'autognome',
            'Bugbear MPMM', 'Centaur MPMM', 'Changeling MPMM',
            'dhampir',  # 'Dhampir Hungers', 'Dhampir Origins',
            'disembodied',
            'dragonborn', 'Dragonborn Variant: Draconbloods', 'Dragonborn Variant: Ravenite',
            'Variant Dragonborn: Chromatic Dragonborn', 'Variant Dragonborn: Metallic Dragonborn',
            'Variant Dragonborn: Gem Dragonborn',
            'dwarf', 'Hill Dwarf', 'Mountain Dwarf', 'Mark of Warding', 'Duergar MPMM',
            # 'Eladrin (Variant)',
            'elf', 'Drow', 'High Elf', 'Wood Elf', 'Eladrin',
            'Shadar-kai',  # 'Elves of Aerenal', 'Aereni Wood Elf', 'Sea Elf',
            'Valenar Wood Elf', 'Mark of Shadow', 'Pallid Elf', 'Eladrin MPMM', 'Sea Elf MPMM',
            'Shadar-Kai MPMM', 'Elf Variant: Astral Elf', 'fairy', 'firbolg',
            'Firbolg MPMM',
            # 'genasi',
            'Genasi (Air) MPMM', 'Genasi (Earth) MPMM', 'Genasi (Fire) MPMM', 'Genasi (Water) MPMM',
            'giff',
            'gith',
            'Githyanki MPMM', 'Githzerai MPMM',
            'gnome', 'Forest Gnome', 'Rock Gnome', 'Born of Deep Earth', 'Master Miners',
            # 'Deep Dwellers', 'Scouts and Spies', 'Deep Gnome Names', 'Deep Gnome Traits',
            # 'Mark of Scribing',
            'Deep Gnome MPMM',
            'Goblin MPMM',
            'Goliath MPMM', 'hadozee',
            'half-elf', 'Variant Half-Elf: Aquatic Elf Descent)',
            'Variant Half-Elf: Drow Descent)',
            'Variant Half-Elf: Moon Elf or Sun Elf Descent)',
            'Variant Half-Elf: Wood Elf Descent)', 'Variant Half-Elf: Mark of Detection',
            'Variant Half-Elf: Mark of Storm',
            'half-orc', 'Variant Half-Orc: Mark of Finding',
            'halfling', 'Lightfoot Halfling', 'Stout Halfling', 'Ghostwise Halfling',
            'Mark of Healing', 'Mark of Hospitality', 'Lotusden Halflings',
            'Harengon Traits',
            'hexblood', 'Hexblood Origins', 'Becoming a Hag',
            'Hobgoblin MPMM',
            'human', 'Variant Human',
            'Variant Human: Mark of Finding', 'Variant Human: Mark of Handling',
            'Variant Human: Mark of Making', 'Variant Human: Mark of Passage',
            'Variant Human: Mark of Sentinel',
            'kalashtar', 'kender',
            'Kenku MPMM', 'Kobold MPMM', 'leonin',
            'Lizardfolk MPMM', 'loxodon', 'mapach',
            'Minotaur MPMM', 'Orc MPMM',
            'owlin', 'plasmoid', 'reborn',  # 'Lost Memories', 'Reborn Origins',
            'Satyr MPMM',
            'Shifter MPMM', 'simic-hybrid',  # 'Animal Enhancement',
            'strig', 'Stout Strig',
            'Swift Strig',  'Tabaxi MPMM', 'thri-kreen',
            'tiefling', 'Bloodline of Asmodeus', 'Bloodline of Baalzebul',
            'Bloodline of Dispater', 'Bloodline of Fierna', 'Bloodline of Glasya',
            'Bloodline of Levistus', 'Bloodline of Mammon', 'Bloodline of Mephistopheles',
            'Bloodline of Zariel',  # 'Tiefling Variants',
            'Variant Tiefling: Feral',
            "Variant Tiefling: Devil's Tongue",
            'Variant Tiefling: Hellfire', 'Variant Tiefling: Winged',
            'Tortle MPMM', 'Triton MPMM', 'vedalken', 'verdan', 'warforged', 'wechselkind',
            'Yuan-Ti MPMM']

dfRace = loadDataFrame('./races/allRaces.csv')
dfRace = dfRace[dfRace['subrace'].isin(listRace)]
# listRaceCombined = [ i + ' ' + j for i,j in zip(list(dfRace['race']), list(dfRace['subrace']) )]

listRaceCombined = combine_columns_to_list(dfRace, 'race', 'subrace')

st.selectbox(
    "Quelle est votre Race ? ",
    [select]+sorted(listRaceCombined),
    key='race',
    on_change=enoughInfo
)

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
    "Barbarian": 'Barbare',
    "Bard": 'Barde',
    "Cleric": 'Pretre',
    "Druid": 'Druide',
    "Fighter": 'Guerrier',
    "Monk": 'Moine',
    "Paladin": 'Paladin',
    "Ranger": 'Rodeur',
    "Rogue": 'Roublard',
    "Sorcerer": 'Sorcier',
    "Warlock": 'Occultiste',
    "Wizard": 'Magicien',
    "Artificer": 'Artificier'
}

listEnFrClass = [i[1] + ' | ' + i[0] for i in dictEnFrClass.items()]

cl1, cl2 = st.columns(2)

with cl1:
    st.selectbox(
        "Quelle est votre classe primaire ? ",
        [select]+listEnFrClass,
        key='classe1',
        on_change=enoughInfo
    )

    if (st.session_state.classe1 != select):
        idx_c1 = listEnFrClass.index(st.session_state['classe1'])

        dfClasse1 = loadDataFrame(
            './classes/'+listClass[idx_c1]+'20tableFull.csv')

        # st.write(dfClasse1)

        st.number_input('Niveau de votre classe primaire',
                        min_value=1, max_value=maxLvl,
                        value=st.session_state['lvl1'], step=1,
                        format=None,
                        key='lvl1',
                        on_change=enoughInfo)
        
        ### sousclasse 1 subclass
        dfSc1 = loadDataFrame(
            './subclasses/'+str.lower(listClass[idx_c1])+'Sc.csv')
        
        lsSc1 = [select]+[  i +' | '+j for i,j in zip(dfSc1['subclass'].unique(),dfSc1['subclass_FR'].unique())]
        
        st.selectbox(label='avec la sous classe',options = lsSc1, key='sousClasse1' )

# %% clss 2 tmp


with cl2:
    st.selectbox(
        "Quelle est votre classe secondaire ? ",
        [select]+listEnFrClass,
        key='classe2',
        on_change=enoughInfo
    )

    if (st.session_state.classe2 != select):
        idx_c2 = listEnFrClass.index(st.session_state['classe2'])

        dfClasse2 = loadDataFrame(
            './classes/'+listClass[idx_c2]+'20tableFull.csv')

        # st.write(dfClasse2)

        st.number_input('Niveau de votre classe secondaire',
                        min_value=1, max_value=maxLvl,
                        value=st.session_state['lvl2'], step=1,
                        format=None,
                        key='lvl2',
                        on_change=enoughInfo)

        ### sousclasse 1 subclass
        dfSc2 = loadDataFrame(
            './subclasses/'+str.lower(listClass[idx_c2])+'Sc.csv')
        
        lsSc2 = [select]+[  i +' | '+j for i,j in zip(dfSc2['subclass'].unique(),dfSc2['subclass_FR'].unique())]
        
        st.selectbox(label='avec la sous classe',options = lsSc2, key='sousClasse2' )


# %% historique

dfBG = loadDataFrame('./backgrounds/dfBackground.csv')

# listBG_EnFr = [ row['background FR'] + ' | '+ row['background'] + ' ' + row['skills'] for idx,row in dfBG.iterrows() ]

listBG_EnFr = []

for idx, row in dfBG.iterrows():
    listBG_EnFr.append(row['background FR'] + ' | ' +
                       row['background'] + ' ' + row['skills'])

st.selectbox(
    "Quelle est votre historique ? ",
    [select]+listBG_EnFr,
    key='historique',
    on_change=enoughInfo
)

# %% Dons

dfFeat = loadDataFrame('./feats/featTable.csv')

listFeat_EnFr = []

for idx, row in dfFeat.iterrows():
    listFeat_EnFr.append(row['Dons'] + ' | ' + row['Feat'])


st.multiselect(
    "Quelle sont vos dons ? ",
    listFeat_EnFr,
    key='dons',
    on_change=enoughInfo
)

# %% new part

st.write('==============================CETTE PARTIE EST NON OBLIGATOIRE POUR LE MOMENT====================================')

st.text_input('Mettre ici le lien discord vers vos jet de stat',
              key='discordStat')

st.write('Entrez vos stats de **BASE** (avant tout modificateur)')

colStat = st.columns(6)
statsName = ['FOR', 'DEX', 'CON', 'INT', 'SAG', 'CHA']

for c, s in zip(colStat, statsName):
    with c:
        st.number_input(s, min_value=4, max_value=18, value=10, step=1, key=s)

#%%

st.multiselect(label='Selectionnez vos bonus de race (3 au choix)',
               options=['FOR +1', 'FOR +1', 'DEX +1', 'DEX +1', 'CON +1', 'CON +1', 'INT +1', 'INT +1', 'SAG +1', 'SAG +1', 'CHA +1', 'CHA +1',], key='bonusRacial',
               max_selections=3)

# %% test bonus dons


def detect_stats_in_string(input_string):
    # List of D&D stat abbreviations in the order they correspond to a list of 6 elements
    stats = ['str', 'con', 'dex', 'int', 'wis', 'cha']

    # Detect which stats are present in the input string (case insensitive)
    present_stats = [stat for stat in stats if stat in input_string.lower()]

    # Return the indices of the detected stats
    return [stats.index(stat) for stat in present_stats]


lsDonsNoAsi = [d for d in st.session_state['dons'] if not 'ASI' in d]
for i in lsDonsNoAsi:
    # dfFeat[]
    # st.write(listFeat_EnFr.index(i))

    bonusStr = dfFeat.iloc[listFeat_EnFr.index(i)]['Bonus']
    listStat = detect_stats_in_string(bonusStr.lower())

    # st.write(listStat)

    st.selectbox(label=i, options=[statsName[x] for x in listStat], key=i)

### dons ASI [item for item in original_list for _ in range(2)]

lsDonsAsi = [d for d in st.session_state['dons'] if 'ASI' in d]
for i in lsDonsAsi:
    # dfFeat[]
    # st.write(listFeat_EnFr.index(i))

    # bonusStr = dfFeat.iloc[listFeat_EnFr.index(i)]['Bonus']
    # listStat = detect_stats_in_string(bonusStr.lower())

    # st.write(listStat)

    st.multiselect(label=i, options=['str','str', 'dex','dex','con','con', 'int','int', 'wis','wis', 'cha','cha'], key=i,
                   max_selections=2)

listBonusDons = [st.session_state[d] for d in lsDonsNoAsi] + [i  for d in lsDonsAsi for i in st.session_state[d]] 
# %% new part : PV

st.write('==================================================================')

st.write('Vous pouvez entrez vos PV par niveau (sans bonus de CON) ci-dessous')
st.write('Pour rappel les PVs de votre 1er niveau sont maxés automatiquement')

colPv1,colPv2,colPv3,colPv4 = st.columns(4)

with colPv1:st.number_input(label='PV niveau 2', min_value=1, max_value=12, value=1, step=None,key='pv1')

with colPv2:st.number_input(label='PV niveau 3', min_value=1, max_value=12, value=1, step=None,key='pv2')

with colPv3:st.number_input(label='PV niveau 4', min_value=1, max_value=12, value=1, step=None,key='pv3')
          
with colPv4:st.number_input(label='PV niveau 5', min_value=1, max_value=12, value=1, step=None,key='pv4')
   

st.write('Vous pouvez également mettre le lien vers vos jet de PV ici')
st.text_input(label='Vous pouvez également mettre le lien vers vos jet de PV ici',value='',key='discordPV')

# %% new part

st.write('==================================================================')

st.write('Parlons un peu de vous...')

st.text_input(label="Décrivez l'apparence de votre personnage",
              key='character_appearance')

st.text_input(label="Parlez nous de son histoire (backstory)",
              key='character_backstory ')

st.text_input(label="Et concernant ses alliées ? Ses allégeances ? Des organisations ?",
              key='allies_and_organization ')

st.text_input(label="Quels sont ses idéaux et ses buts ?", key='ideals ')

st.text_input(label="Et ses liens ?", key='bonds')

st.text_input(
    label="Toutes légende a ses défauts, partagez les donc", key='flaws')

#  à changer en double choix
dnd_alignments = {
    "Lawful Good": "Loyal Bon",
    "Neutral Good": "Neutre Bon",
    "Chaotic Good": "Chaotique Bon",
    "Lawful Neutral": "Loyal Neutre",
    "True Neutral": "Neutre Neutre",
    "Chaotic Neutral": "Chaotique Neutre",
    "Lawful Evil": "Loyal Mauvais",
    "Neutral Evil": "Neutre Mauvais",
    "Chaotic Evil": "Chaotique Mauvais"
}

#lsAlignment = [i[1] + ' | ' + i[0] for i in dnd_alignments.items()]
lsAlignment = [i[1] + ' | ' + i[0] for i in dnd_alignments.items()]

st.selectbox(
    label="tout cela nous dépeint quelqu'un de quel alignement ?",options=lsAlignment, key='Alignment')
#%% 

dnd_classes_hit_dice = {
    "Barbarian": 12,
    "Bard": 8,
    "Cleric": 8,
    "Druid": 8,
    "Fighter": 10,
    "Monk": 8,
    "Paladin": 10,
    "Ranger": 10,
    "Rogue": 8,
    "Sorcerer": 6,
    "Warlock": 8,
    "Wizard": 6
}
# %% button

enoughInfo()

# st.write(allInfo)
buttonText = 'Il manques des infos, au boulot !'*(not st.session_state['allInfo']) + \
    'Il y a toutes les informations (minimales) necessaire pour creer votre fiche !'*(
        st.session_state['allInfo'])

buttonActiv = st.button(buttonText,
                        key=None, disabled=not st.session_state['allInfo'])

if (buttonActiv):
    # st.write('BINGO')

    # if(st.session_state['classe2']==select):
    #     st.session_state['classe2']=''

    if (st.session_state['classe2'] == select):
        class2obj = ''
    else:
        class2obj = st.session_state['classe2'].split()[-1]
        
    if (st.session_state['sousClasse2'] == select):
        subClass2obj = ''
    else:
        subClass2obj = st.session_state['sousClasse2'].split()[0]

    listDonsInput = []

    for i in st.session_state['dons']:
        listDonsInput.append(dfFeat.iloc[listFeat_EnFr.index(i)]['Feat'])

    # st.write(st.session_state['dons'],'>>>', [ i.split()[-1] for i in st.session_state['dons'] ] )

    # current_race = list(dfRace['subrace'])[
    #     listRaceCombined.index(st.session_state['race'])]

    # data = buildCharacterV1(nomPerso=st.session_state['nom'],
    #                         stats=[], pvs=[],
    #                         # subrace=st.session_state['sousrace'],
    #                         race=current_race,
    #                         class1=st.session_state['classe1'].split()[-1], lvl1=int(st.session_state['lvl1']),
    #                         class2=class2obj, lvl2=int(st.session_state['lvl2']),
    #     background=str.lower(dfBG.iloc[listBG_EnFr.index(
    #         st.session_state['historique'])]['background']),
    #     feats=listDonsInput,
    #     fileName='newFile')
    
    
    
    stat_count = {'FOR':0, 'DEX':0, 'CON':0, 'INT':0, 'SAG':0, 'CHA':0}

    # Parcours de la liste
    for item in st.session_state['bonusRacial']:
        # Extraire la statistique (avant le '+1')
        stat = item.split()[0]
        # Incrémenter le compteur correspondant
        stat_count[stat] += 1
    
    stat_count_feat = {'FOR':0, 'DEX':0, 'CON':0, 'INT':0, 'SAG':0, 'CHA':0}
    for i in listBonusDons:
        if(i):
            stat_count_feat[i.upper()]+=1
        
    stats = {
            'strength' :        {'flat': st.session_state['FOR'], 'race':stat_count['FOR'], 'feat':stat_count_feat['FOR']},
            'dexterity' :       {'flat': st.session_state['DEX'], 'race':stat_count['DEX'], 'feat':stat_count_feat['DEX']},
            'constitution' :    {'flat': st.session_state['CON'], 'race':stat_count['CON'], 'feat':stat_count_feat['CON']},
            'intelligence' :    {'flat': st.session_state['INT'], 'race':stat_count['INT'], 'feat':stat_count_feat['INT']},
            'wisdom' :          {'flat': st.session_state['SAG'], 'race':stat_count['SAG'], 'feat':stat_count_feat['SAG']},
            'charisma' :        {'flat': st.session_state['CHA'], 'race':stat_count['CHA'], 'feat':stat_count_feat['CHA']},
        }
    
    
    pvs = [ dnd_classes_hit_dice[st.session_state['classe1'].split()[-1]],
            st.session_state['pv1'],
            st.session_state['pv2'],
            st.session_state['pv3'],
            st.session_state['pv4'],
            ]
    
    data = buildCharacterV2(nomPerso=st.session_state['nom'],
                            stats=stats, discStats=st.session_state['discordStat'], 
                            pvs=pvs, discPvs=st.session_state['discordPV'], 
                            race=st.session_state['race'], 
                            class1=st.session_state['classe1'].split()[-1], sc1=st.session_state['sousClasse1'].split()[0], lvl1=int(st.session_state['lvl1']), 
                            class2=class2obj, sc2=subClass2obj, lvl2=int(st.session_state['lvl2']), 
                            background=str.lower(dfBG.iloc[listBG_EnFr.index(st.session_state['historique'])]['background']), 
                            feats=listDonsInput,
                         character_appearance=st.session_state['character_appearance'],
                         character_backstory=st.session_state['character_backstory'],
                         allies_and_organization=st.session_state['allies_and_organization'],
                         ideals=st.session_state['ideals'],
                         bonds=st.session_state['bonds'],
                         flaws=st.session_state['flaws'],
                         Alignment=st.session_state['Alignment'],
                         fileName='newFile')

    json_string = json.dumps(data)

    # st.json(json_string, expanded=True)

    st.download_button(
        label="Téléchargez votre personnage !",
        file_name=st.session_state['nom']+".json",
        mime="application/json",
        data=json_string,
    )

    st.write('finito')

# %% download part

# json_string = json.dumps(data)

# st.json(json_string, expanded=True)

# st.download_button(
#     label="Download JSON",
#     file_name="data.json",
#     mime="application/json",
#     data=json_string,
# )
