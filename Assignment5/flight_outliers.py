
#@author : Ying liu
# coding: utf-8
import bs4
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import datetime
from unidecode import unidecode
from dateutil.parser import parse

import scipy as sp
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler, MaxAbsScaler
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import euclidean
%matplotlib inline

# Task 1
def scrape_data(start_date, from_place, to_place, city_name):
    driver = webdriver.Chrome()
    # driver = webdriver.Chrome()
    driver.get('https://www.google.com/flights/explore/')
    
    from_input = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]/div/div')
    from_input.click()
    
    actions = ActionChains(driver)
    actions.send_keys(from_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    
    to_input = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[4]/div/div')
    
    to_input.click()
    
    actions = ActionChains(driver)
    actions.send_keys(to_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    
    time.sleep(1)
    
    url = driver.current_url[:-10] + start_date.strftime("%Y-%m-%d")
    print url
    driver.get(url)
    
    time.sleep(2)
    
    results = driver.find_elements_by_class_name('LJTSM3-v-d')
    test = results[0]
    
    for r in results:
        test = r
        city = unidecode(test.find_elements_by_class_name('LJTSM3-v-c')[0].text)
        if city.find(city_name) != -1:
            print 'find!!'
            print city
            break
            
    bars = test.find_elements_by_class_name('LJTSM3-w-x')
    
    data = []
    for bar in bars:
        ActionChains(driver).move_to_element(bar).perform()
        time.sleep(0.001)
        data.append((test.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[0].text,
                     test.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[1].text))
    data[-5:]
    d = data[0]
    clean_data = [(float(d[0].replace('$', '').replace(',', '')), (parse(d[1].split('-')[0].strip()))) for d in data]
    df = pd.DataFrame(clean_data, columns=['Price', 'Date_of_Flight'])
    
    return df


# Task 2
def scrape_data_90(start_date, from_place, to_place, city_name):
    data_60 = scrape_data(start_date, from_place, to_place, city_name)
    start_date = start_date + datetime.timedelta(days=60)
    data_90 = scrape_data(start_date, from_place, to_place, city_name)
    return pd.concat([data_60,data_90[:30]],ignore_index=True)

# Task 3
def task_3_dbscan(flight_data):
    flight_data['Day'] = (flight_data['Date_of_Flight'] - flight_data['Date_of_Flight'][0]).dt.days
    day = np.array(flight_data['Day'],dtype = pd.Series)
    price = np.array(flight_data['Price'],dtype = pd.Series)
    array = np.concatenate([day[:, None], price[:, None]], axis=1) 
    X = StandardScaler().fit_transform(array)
   
    # run dbscan
    # find clusters
    db = DBSCAN(eps= .4, min_samples=3).fit(X)  
     
    labels = db.labels_
    flight_data['labels'] = labels
    
    #number of cluster
    n_clusters = len(set(labels)) 
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    plt.subplots(figsize=(12,8))
    
    for k, c in zip(unique_labels, colors):
        class_member_mask = (labels == k) 
        xy = X[class_member_mask] 
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c,
                 markeredgecolor='k', markersize=14)
    plt.title("Total Clusters: {}".format(n_clusters), fontsize=14,y=1.01)
    
    # save image
    plt.savefig('/Users/admin/BIA660C-Assignment/Assignment5/task_3_dbscan.png')
    
    # find noise point
    noise_points = flight_data['Price'][flight_data['labels'] == -1]
    print noise_points #series 
    
    lbls = np.unique(db.labels_)
    cluster_means = [np.mean(array[labels==num, :], axis=0) for num in lbls if num != -1] 
    # print "Cluster Means: {}".format(cluster_means)
    
    # euclidean distance
    dists = []
    for point in noise_points:
        dists.append([euclidean(point, cm) for cm in cluster_means])
    
    # closest cluster for each noise point
    cluster_labels = [] 
    for dist in dists:
        for index, value in enumerate(dist):
            if value == min(dist):
                cluster_labels.append(index)
            
    closest_cluster_means = [np.mean(array[labels==num, 1], axis=0) for num in cluster_labels] # mean of closest cluster
    closest_cluster_std = [np.std(array[labels==num, 1], axis=0) for num in cluster_labels] # std of closest cluster
    
    price_mean = []
    price_std = []
   
    for val in closest_cluster_means:
        price_mean.append(val)
    for val in closest_cluster_std:
        price_std.append(val)
 
    # find outlier
    outliers = []
    for noise_point,mean,std in zip(noise_points,price_mean,price_std):
        if noise_point + 50 > mean and noise_point > mean - 2 * std:
            outliers.append(noise_point)
    
    for outlier in outliers:
        Days = flight_data['Day'][flight_data['Price'] == outlier]
    
    data = [{'Day': Days.values},{'Outlier': outliers}]
    
    df_outlier = pd.DataFrame([[Days.values, outliers]], columns = ['Day','Outlier'])
    print df_outlier


def task_3_IQR(flight_data):
    Q1 = flight_data['Price'].quantile(.25)
    Q3 = flight_data['Price'].quantile(.75)
    IQR = Q3 - Q1
    
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    
    color = dict(boxes='DarkGreen', whiskers='DarkOrange', medians='DarkBlue', caps='Gray')
    flight_data['Price'].plot.box(color=color, sym='r+')
    
    plt.savefig('/Users/admin/BIA660C-Assignment/Assignment5/task_3_iqr.png')
    
    return flight_data[flight_data['Price'] < lower]

# Task 4
def task_4_dbscan(flight_data):
    flight_data['Day'] = (flight_data['Date_of_Flight'] - flight_data['Date_of_Flight'][0]).dt.days
    day = np.array(flight_data['Day'],dtype = pd.Series)
    # set x as scale, x<sqrt(x^2+400)<2x
    # origin (0,0) represent 0day and 0price
    # select scale as 30
    day = day * 30 # do the scaling 
    price = np.array(flight_data['Price'],dtype = pd.Series)
    X = np.concatenate([day[:, None], price[:, None]], axis=1) 
    
    # run DBSCAN
    # find clusters
    # a = 30 (represent the difference between continuous two days)
    # b = 20 (the difference between prices within continuous two days should be no more than 20)
    # sqrt(a^2 + b^2) = 36.055
    # if the distance from (30,21) [this point should not be included] to original point should be euclidean distance
    # euclidean distance: 36.61966684720111
    # epsilon can be [36.055,36.61966684720111]
    db = DBSCAN(eps= 36.4, min_samples=3).fit(X)  
    # only if min_samples <= 3, there would be more than 1 clusters
    
    labels = db.labels_
    unique_labels = set(labels) 
    flight_data['labels'] = labels
    
    #plot
    #number of cluster
    n_clusters = len(set(labels)) 
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    plt.subplots(figsize=(12,8))
    
    for k, c in zip(unique_labels, colors):
        class_member_mask = (labels == k) 
        xy = X[class_member_mask] 
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c,
                 markeredgecolor='k', markersize=14)
    plt.title("Total Clusters: {}".format(n_clusters), fontsize=14,y=1.01)
    
    # return the 5 day period with the lowest average price for each cluster
    cluster_lens = []
    clusters_5 = []
    for cluster_label in unique_labels:
        cluster = flight_data[flight_data['labels'] == cluster_label]
        cluster_len = len(cluster.index)
        if cluster_label != -1:
            cluster_lens.append(cluster_len)
            
    # test if the length of each cluster is larger than 5
            if cluster_len >= 5:
                avg_5days_min = 1000000
                min_days = []
                for start_index in range(0, cluster_len - 4):
                    end_index = start_index + 5
                    cluster_5days = cluster[start_index : end_index]
                    avg_5days = cluster_5days['Price'].mean()
                    if avg_5days_min < avg_5days:
                        avg_5days_min = avg_5days_min

                    else:
                        avg_5days_min = avg_5days
                        min_days = cluster_5days
   
                print " Returned Cluster label: {}".format(cluster_label) 
                print " The lowest average price: {}".format(avg_5days_min)
                #print min_days
                
                # return periods where the difference between minimum price and the maximum price is also <= $20.
                if min_days['Price'].max() - min_days['Price'].min() < 20:
                    clusters_5.append(min_days)
    return clusters_5


# Test

print("************************ Task1 ********************************")
fare = scrape_data(parse('2017-05-03'),'JFK','Europe','Malaga')
print(fare)

print("************************ Task2 ********************************")
fare_90 = scrape_data_90(parse('2017-05-03'),'JFK','Europe','Malaga')
print(fare_90)

print("************************ Task3 ********************************")

print (task_3_dbscan(fare_90))

print("************************ Task3 Q2********************************")

print (task_3_IQR(fare_90))

print("************************ Task4 ********************************")

print (task_4_dbscan(fare_90))