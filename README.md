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

## Capteurs

### Capteur de température

L'intégration crée automatiquement un capteur de température qui lit les données depuis le topic MQTT :
- **Topic** : `{prefix}/temperature`
- **Format** : Valeur numérique en Celsius
- **Exemple** : `poolnexus/temperature` avec la valeur `25.5`

## Topics MQTT

L'intégration s'abonne aux topics suivants :

- `{prefix}/temperature` : Température en Celsius

## Support

Pour le support et les questions, veuillez créer une issue sur le repository GitHub.
