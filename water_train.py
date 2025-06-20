import pandas as pd
import numpy as np
import mlflow
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import dagshub

dagshub.init(repo_owner='githubshaurya', repo_name='mlflow_exp_dagshub', mlflow=True)

mlflow.set_experiment("water_exp2")
mlflow.set_tracking_uri("https://dagshub.com/githubshaurya/mlflow_exp_dagshub.mlflow")
data = pd.read_csv(r"/mnt/c//NLP_practice/python_learn/MLOps/mlflow_exp/data/water_potability.csv")

data.isnull().sum()


from sklearn.model_selection import train_test_split
train_data,test_data = train_test_split(data,test_size=0.20,random_state=42)

def fill_missing_with_median(df):
    for column in df.columns:
        if df[column].isnull().any():
            median_value = df[column].median()
            df[column].fillna(median_value,inplace=True)
    return df


# Fill missing values with median
train_processed_data = fill_missing_with_median(train_data)
test_processed_data = fill_missing_with_median(test_data)

from sklearn.ensemble import GradientBoostingClassifier
import pickle
X_train = train_processed_data.iloc[:,0:-1].values
y_train = train_processed_data.iloc[:,-1].values

n_estimators = 775

with mlflow.start_run():
    clf = GradientBoostingClassifier(n_estimators=n_estimators)
    clf.fit(X_train,y_train)

    # save 
    pickle.dump(clf,open("model.pkl","wb"))

    X_test = test_processed_data.iloc[:,0:-1].values
    y_test = test_processed_data.iloc[:,-1].values

    from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score

    model = pickle.load(open('model.pkl',"rb"))

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test,y_pred)
    precision = precision_score(y_test,y_pred)
    recall = recall_score(y_test,y_pred)
    f1_score = f1_score(y_test,y_pred)

    mlflow.log_metric("acc",acc)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1-score",f1_score)
    mlflow.log_param("n_estimators: ",n_estimators)
    
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10,8))
    sns.heatmap(cm, annot=True, cmap="YlGnBu", fmt="d")
    plt.xlabel("predicted")
    plt.ylabel("actual")
    plt.show()
    plt.title("Confusion Matrix")
    plt.savefig("Confusion_matrix.png")
    mlflow.log_artifact("Confusion_matrix.png")
    # mlflow.sklearn.log_model(clf, "GradientBoostingClassifier")
    mlflow.log_artifact(__file__)
    mlflow.set_tag("Author", "Datathinkers")
    mlflow.set_tag("model", "GB")
