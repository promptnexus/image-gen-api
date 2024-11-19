/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("4qaxoe6y9o4jgpo")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "lsn4l9i3",
    "name": "isAdmin",
    "type": "bool",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {}
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("4qaxoe6y9o4jgpo")

  // remove
  collection.schema.removeField("lsn4l9i3")

  return dao.saveCollection(collection)
})
