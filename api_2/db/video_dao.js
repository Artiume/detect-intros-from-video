const MongoClient = require('mongodb').MongoClient;

dbname = process.env.db_name
url = process.env.db_url
const collectionKey = 'videos';

module.exports = class VideosDao {

     /**
     * Combines multiple queries and puts a pagination filter on top of it to reduce traffic  
      * @param {*} queryArray 
      * @param {*} page 
      * @param {*} limit 
      */
    static findByMultipleQueries(queryArray, page, limit) {
        return new Promise(function (resolve, reject) {
            MongoClient.connect(url, function(err, db) {
                if (err) 
                    reject(err);
                else {
                    db.db(dbname).collection(collectionKey).find({
                        "$and": queryArray 
                    }).skip(page*limit).limit(limit).toArray(function (err, res) {
                        if (err) {
                            console.log(err);
                            resolve([]);
                        }                       
                        resolve(res);
                    });
                }
            });
        });
    }

    /**
     * Updates the annotaed intro of a video by querying for the video download url 
     * @param {*} url 
     * @param {*} start 
     * @param {*} end 
     */
    static setIntro(url, start, end) {
        query = {url: url}
        update = { $set: { start: start, end: end } }
        return new Promise(function (resolve, reject) {
            MongoClient.connect(url, function(err, db) {
                if (err) 
                    reject(err);
                else {
                    dbo.collection(collectionKey).updateOne(query, update, function(err, res) {
                        if (err) 
                            reject(err)
                        resolve(res)
                        db.close();
                    });
                }
            });
        });
    }


}
    
