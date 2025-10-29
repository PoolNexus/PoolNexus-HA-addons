# PoolNexus HA Addons

Intégration Home Assistant pour les dispositifs PoolNexus via MQTT.

IMPORTANT: Les topics MQTT sont namespacés par appareil pour éviter les
collisions quand plusieurs PoolNexus partagent le même broker. Le format
obligatoire est :

```
<mqtt_topic_prefix>/<serialNumber>/<resource>
```

Le champ `serial` (numéro de série) doit être renseigné lors de la
configuration (via le config flow). L'intégration s'attend explicitement au
numéro de série pour construire les topics.

Voir `MQTT-TOPICS.md` (FR) et `MQTT-TOPICS-EN.md` (EN) pour la liste complète des
topics et des exemples.

Liens utiles :
- Version anglaise du README : `README-EN.md`
- MQTT topics (EN) : `MQTT-TOPICS-EN.md`

## Installation

Cette intégration peut être installée via HACS (Home Assistant Community Store).

1. Ajoutez ce repository à HACS
2. Installez l'intégration
3. Redémarrez Home Assistant
4. Ajoutez l'intégration via Configuration > Intégrations

## Configuration

### Configuration via l'interface utilisateur

1. Allez dans Configuration > Intégrations
2. Cliquez sur "Ajouter une intégration"
3. Recherchez "PoolNexus"
4. Configurez les paramètres MQTT :
   - **Broker MQTT** : Adresse IP ou nom d'hôte du broker MQTT
   - **Port** : Port du broker MQTT (défaut: 1883)
   - **Nom d'utilisateur** : Nom d'utilisateur MQTT (optionnel)
   - **Mot de passe** : Mot de passe MQTT (optionnel)
   - **Préfixe du topic** : Préfixe des topics MQTT (défaut: poolnexus)

### Configuration manuelle

Vous pouvez également configurer l'intégration via `configuration.yaml` :

```yaml
poolnexus:
  mqtt_broker: "192.168.1.100"
  mqtt_port: 1883
  mqtt_username: "mqtt_user"
  mqtt_password: "mqtt_password"
  mqtt_topic_prefix: "poolnexus"
```

## Entités créées

### Capteurs

#### Capteur de température
- **Topic** : `{prefix}/{serialNumber}/temperature`
- **Format** : Valeur numérique en Celsius
- **Exemple** : `poolnexus/PN0001/temperature` avec la valeur `25.5`

#### Capteur de pH
- **Topic** : `{prefix}/{serialNumber}/ph`
- **Format** : Valeur numérique en pH
- **Exemple** : `poolnexus/PN0001/ph` avec la valeur `7.2`

#### Capteur de chlore
- **Topic** : `{prefix}/{serialNumber}/chlorine`
- **Format** : Valeur numérique en mV
- **Exemple** : `poolnexus/PN0001/chlorine` avec la valeur `0.802`

#### Capteur de niveau d'eau
- **Topic** : `{prefix}/{serialNumber}/water_level`
- **Format** : `ok` ou `nok`
- **Exemple** : `poolnexus/PN0001/water_level` avec la valeur `nok`

#### Capteur de niveau de chlore
- **Topic** : `{prefix}/{serialNumber}/chlorine_level`
- **Format** : `low`, `no liquid` ou `ok`
- **Exemple** : `poolnexus/PN0001/chlorine_level` avec la valeur `ok`

#### Capteur de niveau de pH
- **Topic** : `{prefix}/{serialNumber}/ph_level`
- **Format** : `low`, `no liquid` ou `ok`
- **Exemple** : `poolnexus/PN0001/ph_level` avec la valeur `low`

### Switches

#### Électrovanne
- **Topic de commande** : `{prefix}/{serialNumber}/electrovalve/set`
- **Format** : `ON` ou `OFF`
- **Exemple** : Publier `ON` sur `poolnexus/PN0001/electrovalve/set` pour ouvrir

#### Remplissage automatique
- **Topic de commande** : `{prefix}/{serialNumber}/auto_fill/set`
- **Format** : `ON` ou `OFF`
- **Exemple** : Publier `ON` sur `poolnexus/PN0001/auto_fill/set` pour activer

#### Pompe de circulation
- **Topic de commande** : `{prefix}/{serialNumber}/pump/set`
- **Format** : `ON` ou `OFF`
- **Exemple** : Publier `ON` sur `poolnexus/PN0001/pump/set` pour activer

#### Switch 1
- **Topic de commande** : `{prefix}/{serialNumber}/switch_1/set`
- **Format** : `ON` ou `OFF`
- **Exemple** : Publier `ON` sur `poolnexus/PN0001/switch_1/set` pour activer

#### Switch 2
- **Topic de commande** : `{prefix}/{serialNumber}/switch_2/set`
- **Format** : `ON` ou `OFF`
- **Exemple** : Publier `ON` sur `poolnexus/PN0001/switch_2/set` pour activer

#### State
- **Topic de commande** : `{prefix}/{serialNumber}/{switch}/state`
- **Format** : `ON` ou `OFF`
- **Exemple** : `poolnexus/PN0001/{switch}/state` pour récueperer l'etat du switch


### Text (Valeurs de configuration)

#### Valeur pH cible
- **Topic de commande** : `{prefix}/{serialNumber}/set_ph/set`
- **Format** : `XX.X` (ex: `07.2`)
- **Exemple** : Publier `07.2` sur `poolnexus/PN0001/set_ph/set`

#### Valeur Redox cible
- **Topic de commande** : `{prefix}/{serialNumber}/set_redox/set`
- **Format** : `X.XXX` (ex: `6.500`)
- **Exemple** : Publier `6.500` sur `poolnexus/PN0001/set_redox/set`

#### Température cible
- **Topic de commande** : `{prefix}/{serialNumber}/set_temperature/set`
- **Format** : `XX.X` (ex: `25.0`)
- **Exemple** : Publier `25.0` sur `poolnexus/PN0001/set_temperature/set`

### Information (à lire par l'integrations)

#### Firmware
- **Topic de commande** : `{prefix}/{serialNumber}/firmware`
- **Format** : `X.X.X`
- **Exemple** : Lire sur `poolnexus/PN0001/firmware`

#### Dernière Calibration sonde pH
- **Topic de commande** : `{prefix}/{serialNumber}/last_pH_prob_cal`
- **Format** : `DD/MM/YY HH:MM`
- **Exemple** : Lire sur `poolnexus/PN0001/last_pH_prob_cal`

#### Dernière Calibration sonde ORP
- **Topic de commande** : `{prefix}/{serialNumber}/last_ORP_prob_cal`
- **Format** : `DD/MM/YY HH:MM`
- **Exemple** : Lire sur `poolnexus/PN0001/last_ORP_prob_cal`

#### Disponibility
- **Topic de commande** : `{prefix}/{serialNumber}/availability`
- **Format** : `online` ou `offline`
- **Exemple** : Lire sur `poolnexus/PN0001/availability`

### Alert
- **Topic de commande** : `{prefix}/{serialNumber}/alert`
- **Format** : `{"type": "ph_high", "message": "pH trop élevé", "timestamp": "..."}`
- **Exemple** : Lire sur `poolnexus/PN0001/alert`

### Dernier netoyage de la pompe
- **Topic** : `{prefix}/{serialNumber}/last_pump_cleaning`
- **Format** : `DD/MM/YY HH:MM` (ex: `12/06/24 10:00`)
- **Exemple** : `poolnexus/PN0001/last_pump_cleaning` avec la valeur `12/06/24 10:00`
### Mode de fonctionement (hyvernage passif / hivernage actif / normal)
- **Topic** : `{prefix}/{serialNumber}/operating_mode`
- **Format** : Valeur textuelle indiquant le mode de fonctionnement. Valeurs proposées : `hyvernage_passif`, `hivernage_actif`, `normal`.
- **Exemple** : `poolnexus/PN0001/operating_mode` avec la valeur `normal`
### Verouillage de l'ecran (switch)

- **Topic de commande** : `{prefix}/{serialNumber}/screen_lock/set`
- **Format** : `ON` / `OFF` (ou `locked` / `unlocked` si votre device utilise ces libellés)
- **Exemple** : Publier `ON` sur `poolnexus/PN0001/screen_lock/set` pour verrouiller l'écran
## Topics MQTT

### Topics de lecture (sensors)
- `{prefix}/{serialNumber}/temperature` : Température en Celsius
- `{prefix}/{serialNumber}/ph` : pH de l'eau
- `{prefix}/{serialNumber}/chlorine` : Niveau de chlore en mV
- `{prefix}/{serialNumber}/water_level` : Niveau d'eau (on/off)
- `{prefix}/{serialNumber}/chlorine_level` : État du niveau de chlore (low/no liquid/ok)
- `{prefix}/{serialNumber}/ph_level` : État du niveau de pH (low/no liquid/ok)

### Topics de commande (switches)
- `{prefix}/{serialNumber}/electrovalve/set` : Contrôle de l'électrovanne (ON/OFF)
- `{prefix}/{serialNumber}/auto_fill/set` : Contrôle du remplissage automatique (ON/OFF)

### Topics de configuration (text)
- `{prefix}/{serialNumber}/set_ph/set` : Définir la valeur pH cible (format: XX.X)
- `{prefix}/{serialNumber}/set_redox/set` : Définir la valeur Redox cible (format: X.XXX)
- `{prefix}/{serialNumber}/set_temperature/set` : Définir la température cible (format: XX.X)

## Exemples de données MQTT

### Lecture de capteurs
```json
Topic: poolnexus/PN0001/temperature
Payload: "25.5"

Topic: poolnexus/PN0001/ph
Payload: "7.2"

Topic: poolnexus/PN0001/chlorine
Payload: "1.5"

Topic: poolnexus/PN0001/water_level
Payload: "on"

Topic: poolnexus/PN0001/chlorine_level
Payload: "ok"

Topic: poolnexus/PN0001/ph_level
Payload: "low"
```

### Commandes de switches
```json
Topic: poolnexus/PN0001/electrovalve/set
Payload: "ON"

Topic: poolnexus/PN0001/auto_fill/set
Payload: "OFF"
```

### Configuration des valeurs cibles
```json
Topic: poolnexus/PN0001/set_ph/set
Payload: "07.2"

Topic: poolnexus/PN0001/set_redox/set
Payload: "6.500"

Topic: poolnexus/PN0001/set_temperature/set
Payload: "25.0"
```

## Support

Pour le support et les questions, veuillez créer une issue sur le repository GitHub.
