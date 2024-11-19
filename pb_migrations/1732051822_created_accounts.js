/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "4qaxoe6y9o4jgpo",
    "created": "2024-11-19 21:30:22.922Z",
    "updated": "2024-11-19 21:30:22.922Z",
    "name": "accounts",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "x3p8pzcm",
        "name": "username",
        "type": "email",
        "required": false,
        "presentable": false,
        "unique": false,
        "options": {
          "exceptDomains": null,
          "onlyDomains": null
        }
      },
      {
        "system": false,
        "id": "6vz0ekeq",
        "name": "password",
        "type": "text",
        "required": false,
        "presentable": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
      }
    ],
    "indexes": [],
    "listRule": null,
    "viewRule": null,
    "createRule": null,
    "updateRule": null,
    "deleteRule": null,
    "options": {}
  });

  return Dao(db).saveCollection(collection);
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("4qaxoe6y9o4jgpo");

  return dao.deleteCollection(collection);
})
