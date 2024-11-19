/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("4qaxoe6y9o4jgpo")

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "x3p8pzcm",
    "name": "email",
    "type": "email",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "exceptDomains": null,
      "onlyDomains": null
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("4qaxoe6y9o4jgpo")

  // update
  collection.schema.addField(new SchemaField({
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
  }))

  return dao.saveCollection(collection)
})
