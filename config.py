# config.py

ENV = "DEV"   # change to TEST / PROD later

ENV = "DEV"

CONFIG = {
    "DEV": {
        "SNOW_URL": "https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/Snow-incidents.csv",
        "PTC_URL": "https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/PTC-Cases-Report.csv",
        "AZURE_URL": "https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/All-VCE-Bugs.csv"
    }

"TEST": {
        "SNOW_URL": "https://volvogroup.sharepoint.com/:x:/r/sites/TP-smartarchive/SmartArchive%20Documents/AMS-WINDCHILL/Keshava_L2/Snow-incidents.csv",
        "PTC_URL": "https://volvogroup.sharepoint.com/:x:/r/sites/TP-smartarchive/SmartArchive%20Documents/AMS-WINDCHILL/Keshava_L2/PTC-Cases-Report.csv",
        "AZURE_URL": "https://volvogroup.sharepoint.com/:x:/r/sites/TP-smartarchive/SmartArchive%20Documents/AMS-WINDCHILL/Keshava_L2/All-VCE-Bugs.csv",
}
    "PROD": {
        "SNOW_URL": "https://volvogroup.sharepoint.com/:x:/r/sites/TP-smartarchive/SmartArchive%20Documents/AMS-WINDCHILL/Keshava_L2/Snow-incidents.csv",
        "PTC_URL": "https://volvogroup.sharepoint.com/:x:/r/sites/TP-smartarchive/SmartArchive%20Documents/AMS-WINDCHILL/Keshava_L2/PTC-Cases-Report.csv",
        "AZURE_URL": "https://volvogroup.sharepoint.com/:x:/r/sites/TP-smartarchive/SmartArchive%20Documents/AMS-WINDCHILL/Keshava_L2/All-VCE-Bugs.csv",      
    },

}

    
