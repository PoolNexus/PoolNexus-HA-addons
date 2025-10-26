# PoolNexus HA Addons

Intégration Home Assistant pour les dispositifs PoolNexus via MQTT.

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
- **Topic** : `{prefix}/temperature`
- **Format** : Valeur numérique en Celsius
- **Exemple** : `poolnexus/temperature` avec la valeur `25.5`

#### Capteur de pH
- **Topic** : `{prefix}/ph`
- **Format** : Valeur numérique en pH
- **Exemple** : `poolnexus/ph` avec la valeur `7.2`

#### Capteur de chlore
- **Topic** : `{prefix}/chlorine`
- **Format** : Valeur numérique en mg/L
- **Exemple** : `poolnexus/chlorine` avec la valeur `1.5`

#### Capteur de niveau d'eau
- **Topic** : `{prefix}/water_level`
- **Format** : `on` ou `off`
- **Exemple** : `poolnexus/water_level` avec la valeur `on`

#### Capteur de niveau de chlore
- **Topic** : `{prefix}/chlorine_level`
- **Format** : `low`, `no liquid` ou `ok`
- **Exemple** : `poolnexus/chlorine_level` avec la valeur `ok`

#### Capteur de niveau de pH
- **Topic** : `{prefix}/ph_level`
- **Format** : `low`, `no liquid` ou `ok`
- **Exemple** : `poolnexus/ph_level` avec la valeur `low`

### Switches

#### Électrovanne
- **Topic de commande** : `{prefix}/electrovalve/set`
- **Format** : `ON` ou `OFF`
- **Exemple** : Publier `ON` sur `poolnexus/electrovalve/set` pour ouvrir

#### Remplissage automatique
- **Topic de commande** : `{prefix}/auto_fill/set`
- **Format** : `ON` ou `OFF`
- **Exemple** : Publier `ON` sur `poolnexus/auto_fill/set` pour activer

### Text (Valeurs de configuration)

#### Valeur pH cible
- **Topic de commande** : `{prefix}/set_ph/set`
- **Format** : `XX.X` (ex: `07.2`)
- **Exemple** : Publier `07.2` sur `poolnexus/set_ph/set`

#### Valeur Redox cible
- **Topic de commande** : `{prefix}/set_redox/set`
- **Format** : `X.XXX` (ex: `6.500`)
- **Exemple** : Publier `6.500` sur `poolnexus/set_redox/set`

#### Température cible
- **Topic de commande** : `{prefix}/set_temperature/set`
- **Format** : `XX.X` (ex: `25.0`)
- **Exemple** : Publier `25.0` sur `poolnexus/set_temperature/set`

## Topics MQTT

### Topics de lecture (sensors)
- `{prefix}/temperature` : Température en Celsius
- `{prefix}/ph` : pH de l'eau
- `{prefix}/chlorine` : Niveau de chlore en mg/L
- `{prefix}/water_level` : Niveau d'eau (on/off)
- `{prefix}/chlorine_level` : État du niveau de chlore (low/no liquid/ok)
- `{prefix}/ph_level` : État du niveau de pH (low/no liquid/ok)

### Topics de commande (switches)
- `{prefix}/electrovalve/set` : Contrôle de l'électrovanne (ON/OFF)
- `{prefix}/auto_fill/set` : Contrôle du remplissage automatique (ON/OFF)

### Topics de configuration (text)
- `{prefix}/set_ph/set` : Définir la valeur pH cible (format: XX.X)
- `{prefix}/set_redox/set` : Définir la valeur Redox cible (format: X.XXX)
- `{prefix}/set_temperature/set` : Définir la température cible (format: XX.X)

## Exemples de données MQTT

### Lecture de capteurs
```json
Topic: poolnexus/temperature
Payload: "25.5"

Topic: poolnexus/ph
Payload: "7.2"

Topic: poolnexus/chlorine
Payload: "1.5"

Topic: poolnexus/water_level
Payload: "on"

Topic: poolnexus/chlorine_level
Payload: "ok"

Topic: poolnexus/ph_level
Payload: "low"
```

### Commandes de switches
```json
Topic: poolnexus/electrovalve/set
Payload: "ON"

Topic: poolnexus/auto_fill/set
Payload: "OFF"
```

### Configuration des valeurs cibles
```json
Topic: poolnexus/set_ph/set
Payload: "07.2"

Topic: poolnexus/set_redox/set
Payload: "6.500"

Topic: poolnexus/set_temperature/set
Payload: "25.0"
```

## Support

Pour le support et les questions, veuillez créer une issue sur le repository GitHub.
