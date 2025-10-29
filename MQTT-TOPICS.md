# MQTT — Topics utilisés par l'intégration PoolNexus

Ce document liste les topics MQTT utilisés par l'intégration PoolNexus (fichiers sources : `sensor.py`, `switch.py`, `text.py`, `config_flow.py`). Les topics utilisent désormais le format obligatoire `{prefix}/{serialNumber}/...` — le numéro de série (`serial`) doit être renseigné lors de la configuration.

## Préfixe et segmentation
- Clé de configuration (config flow / entry data) : `mqtt_topic_prefix`
- Valeur par défaut : `poolnexus`
-- Clé requise pour identifier l'appareil : `serial` (string). L'intégration nécessite ce champ pour construire les topics.

Format général des topics
- <mqtt_topic_prefix>/<serialNumber>/<resource>

Exemples (avec `mqtt_topic_prefix = poolnexus` et `serial = SN12345`):

### Capteurs (sensors)
Les sensors s'abonnent à :
- `poolnexus/SN12345/temperature` — température (conversion float)
- `poolnexus/SN12345/ph` — pH (float)
- `poolnexus/SN12345/chlorine` — chlore (float)
- `poolnexus/SN12345/water_level` — niveau d'eau (valeurs textuelles : `on`/`off` ou des labels)
- `poolnexus/SN12345/chlorine_level` — état niveau chlore (textuel)
- `poolnexus/SN12345/ph_level` — état niveau pH (textuel)

Remarque : le code attend des payloads numériques pour les capteurs numériques (float) et des payloads textuels pour certains capteurs d'état.

### Informations (topics en lecture)
En plus des capteurs et commandes, l'intégration lit plusieurs topics d'information :
### Autres informations et état
Quelques topics additionnels fournis par les appareils :
### Switches
Les switches publient sur des topics `.../<switch_type>/set` :
- `poolnexus/SN12345/electrovalve/set` — payload `ON` / `OFF` (publish avec `retain=True`)
- `poolnexus/SN12345/auto_fill/set` — payload `ON` / `OFF` (publish avec `retain=True`)
 - `poolnexus/SN12345/pump/set` — payload `ON` / `OFF` (publish avec `retain=True`)
 - `poolnexus/SN12345/switch_1/set` — payload `ON` / `OFF` (publish avec `retain=True`)
 - `poolnexus/SN12345/switch_2/set` — payload `ON` / `OFF` (publish avec `retain=True`)
- `poolnexus/SN12345/screen_lock/set` — payload `ON` / `OFF` (publish avec `retain=True`)

Les switches utilisent `homeassistant.components.mqtt.async_publish(..., retain=True)`.

### Text entities (valeurs réglables)
Les entités text publient sur `.../<text_type>/set` :
- `poolnexus/SN12345/set_ph/set` — format attendu `\d{2}\.\d` (ex : `07.2`), `retain=True`
- `poolnexus/SN12345/set_redox/set` — format attendu `\d\.\d{3}` (ex : `6.500`), `retain=True`
- `poolnexus/SN12345/set_temperature/set` — format attendu `\d{2}\.\d` (ex : `25.0`), `retain=True`

Les `TextEntity` vérifient le format avant publication et publient en retained pour persistance côté broker.

## Détection automatique (scan) utilisée par le config flow
Le config flow propose une option `scan_devices` qui abonne brièvement l'interface à :
- `<prefix>/#` (ex. `poolnexus/#`) et collecte les premiers segments observés après le préfixe.

Heuristique de détection :
- On suppose que les appareils publient sous `prefix/<serial>/...` (par ex. `poolnexus/SN12345/temperature`).
- Le scan collecte les premiers segments (`SN12345`) et propose la liste à l'utilisateur.
- Le scan fonctionne mieux si les appareils publient des messages retained (les retained messages sont immédiatement livrés à l'abonné).

Si vos appareils n'utilisent pas ce schéma d'annonce, indiquez le topic exact d'annonce (ex. `poolnexus/announce/<serial>` ou `poolnexus/<serial>/info`) pour adapter la détection.

## Notes opérationnelles
- Les topics publiés par les switches et text entities sont envoyés avec `retain=True`. Si vous remplacez la structure des topics (par ex. migration), pensez à nettoyer ou republier les messages retained sur le nouveau chemin.
 - Pour éviter les collisions sur un broker partagé, fournissez `serial` lors de la configuration (champ requis).

## Où trouver la logique dans le code
- `custom_components/poolnexus/sensor.py` — construction des topics et subscription (`async_subscribe`).
- `custom_components/poolnexus/switch.py` — construction des topics et publication (`async_publish` avec `retain=True`).
- `custom_components/poolnexus/text.py` — validation des formats et publication (`async_publish` avec `retain=True`).
- `custom_components/poolnexus/config_flow.py` — option `scan_devices` et gestion du champ `serial`.

---
Si tu veux, je peux :
- Ajouter des exemples concrets avec des serials réels.
- Ajouter une section de migration pour copier les retained messages de l'ancien topic vers le nouveau (attention : opération destructive si mal faite).
- Traduire/adapter ce fichier dans `docs/` ou l'ajouter au README principal.

Dis-moi ce que tu préfères et j'applique la suite.

---
Liens :
- Version anglaise de ce document : `MQTT-TOPICS-EN.md`
- README (FR) : `README.md`
- README (EN) : `README-EN.md`