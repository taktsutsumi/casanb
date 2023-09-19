#!/usr/bin/env python
# coding: utf-8

# converted to a script from jupyter notebook 
####
# # Check contents of the MS data in casatestdata
# 
# When writing new unittests, it is often a bit combersome to figure out if there is suitable MS data already
# exists in casatestdata. 
# This notebook scan subset of the directory contains MS data in casatestdata (either /home/casa or local copy)
# to list some basic parameters (nchan, nspw, nrows, frequencies, etc)
# 
# This uses the inter
# ***

# __Install and Import__
# 
# use local modular casa installion along with jupyter notebook and pandas
# 
#     export PPY=`which python3`
#     virtualenv -p $PPY --setuptools ./local_python3
#     ./local_python3/bin/pip install --upgrade pip
#     ./local_python3/bin/pip install --upgrade numpy matplotlib ipython astropy
#     ./local_python3/bin/pip install --extra-index-url https://casa-pip.nrao.edu/repository/pypi-group/simple casatools
#     ./local_python3/bin/pip install --extra-index-url https://casa-pip.nrao.edu/repository/pypi-group/simple casatasks
#     ./local_python3/bin/pip3 install jupyter
#     ./local_python3/bin/pip3 install pandas
# 
# 
# ***

# __Import Libraries__

# Import required tools/tasks
from casatools import msmetadata
from casatasks import listobs

import os
import numpy as np
import pandas as pd
import glob
import tarfile
from ipywidgets import interact

# Instantiate all the required tools
msmd = msmetadata()

def getmssummary(vis):
    # nspw, nchans, fields, nrows, ncorr¥n",
    nchans=[]
    chan0=[]
    nrow=0
    nspw=0
    fields=[]
    nant=0
    msname=os.path.basename(vis)
    try:
         msmd.open(vis)
         mssummary = msmd.summary()
         nspw = msmd.nspw()
         for ispw in range(nspw):
             nchans.append(msmd.nchan(ispw))
             chan0.append(list(msmd.chanfreqs(ispw,unit='GHz'))[0])
         obs = msmd.observatorynames()[0]
         fields = list(mssummary['fields'])
         nrows = mssummary['nrows']
         nant = msmd.nantennas()
         msmd.close()
         return (obs, nrows, nspw,nchans, chan0, fields, nant)
    except:
         print("%s is not MS. Skip this file" % vis)
         return (0,0,0,0,0,0,0)

def create_paramlists(mslist): 
    '''
    Create parameter lists for all MSes in a list 
    '''

    obsnamelist=[]
    nrowslist=[]
    nspwlist=[]   
    nchanlist=[]
    chan0list=[]
    fieldslist=[]
    msnamelist=[]
    nantlist=[]

    for vis in mslist:
        (obs, nrows, nspw, nchans, chan0, fields, nant) = getmssummary(vis)
        if obs:
            msname = os.path.basename(vis)
            # creat lists
            msnamelist.append(msname)
            nrowslist.append(nrows)
            nspwlist.append(nspw)
            nchanlist.append(nchans)
            chan0list.append(chan0)
            fieldslist.append(fields)
            nantlist.append(nant)
            #print(msname, nspw, nchans, chan0, fields)
    return (msnamelist, nrowslist, nspwlist, nchanlist, chan0list, fieldslist, nantlist) 

# __Generate a list of the MS data__

# Define a function to add a link to the listobs output for each corresponding MS 


def make_clickable(fname):
    return f'<a href="{fname}">"{fname}</a>'

def create_htmltable(subdirname, mslist, excludedlist):
    (msnamelist, nrowslist, nspwlist, nchanlist, chan0list, fieldslist, nantlist) = create_paramlists(mslist)
    #from IPython.display import HTML 
    df = pd.DataFrame({'msname':msnamelist,'nrows':nrowslist, 'nspw':nspwlist,'nchan':nchanlist,'chan0 (GHz)':chan0list,'fields':fieldslist,'nant':nantlist} )
    #pd.set_option('display.max_rows', df.shape[0]+1)    
    #pd.set_option('display.max_colwidth',None)
    df.style.format({"msname":make_clickable})
    df['msname'] = df['msname'].apply(lambda x: f'<a target="_blank", href="{subdirname}_listobs/{x}.listobs.txt">{x}</a>')   
    #display(df)
    #print("MS data in {}".format(datadir+menu.value))
    htmlcontent = df.to_html(escape=False)
    #HTML(htmlcontent)
    #df['msname']

    # save the html to a file and archive with the listobs results to a tarball
    htmlfname = f'testmsdata_list_{subdirname}.html'
    tarfname = f'{htmlfname}.tgz'
    if os.path.exists(tarfname):
        os.remove(tarfname)
    if os.path.exists(htmlfname):
        os.remove(htmlfname)
    print("Write to a html file and create a tar file")   
    with open(htmlfname, 'w') as f:
        f.write(f'ms data in /{subdirname}')
        f.write(htmlcontent)
        f.write(f'Excluded:{excludedlist}')
    with tarfile.open(tarfname, 'x:gz') as tar:
        tar.add(htmlfname)
        tar.add(f'{subdirname}_listobs')
        print(f'tar file {tarfname} created')

# __Point to the casatestdata dir__

datadir='/home/casa/data/casatestdata/measurementset/'


# __Check sub directories__ 

diroptionfull=glob.glob(datadir+'*')
diroption=[os.path.basename(x) for x in diroptionfull]


# __Define interactive drop-down menu for sub-directory selection__

# In[6]:

# some handy functions to use along widgets
#from IPython.display import display, Markdown, clear_output
# widget packages
#import ipywidgets as widgets
# defining some widgets
#text = widgets.Text(
#       value='My Text',
#       description='Title', )
#calendar = widgets.DatePicker(
#           description='Select Date')
#slider = widgets.FloatSlider(
#         value=1,
#         min=0,
#         max=10.0,
#         step=0.1,)
#menu = widgets.Dropdown(
#       options=diroption,
#       value=diroption[0],
#       description=datadir)
#checkbox = widgets.Checkbox(
#           description='Check to invert',)


# __Select subdirectory from the drop-down menu__

# In[7]:

#menu


# Create a directory under the current working directory to store listobs output

# In[8]:

#if os.path.exists(f'{menu.value}_runs'):
#    os.system(f'rm -rf {menu.value}_runs')
#os.system(f'mkdir {menu.value}_runs')
#print(f'Created listobs output directory, {menu.value}_runs')
for dirname in diroption:
    if os.path.exists(f'{dirname}_listobs'):
        os.system(f'rm -rf {dirname}_listobs')
    os.system(f'mkdir {dirname}_listobs')
    print(f'Created listobs output directory, {dirname}_listobs')


# __Run listobs on the MS data in the selected subdirectory__

badmslist = ['uid___A002_X8ca70c_X5_shortened.ms', 
             'expected.bl.ms', 
             'expected.ms',
             'expected.sdsmooth.ms',
             'crosspoltest.ms']             
for subdir in diroptionfull:
    datalist=glob.glob(subdir+'/*')
    subdirname = os.path.basename(subdir)
    print(f'Run listobs for {subdir}')
    validmslist = []
    for vis in datalist:
        visbase = os.path.basename(vis)
        if visbase in badmslist:
            print(f'Skipping {visbase}, as this causes segv')
        else:
            #print('visbase=',visbase)
            try:
                ret=listobs(vis,listfile=f'{subdirname}_listobs/'+visbase+'.listobs.txt')
                validmslist.append(vis)
                del ret
            except:
                print('{} is not valid MS'.format(vis))

    if validmslist:
        excludedlist = [x for x in datalist if x not in validmslist] 
        create_htmltable(os.path.basename(subdir), validmslist, excludedlist)


