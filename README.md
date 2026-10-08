# DocuFlow

**Du document à la donnée fiable.**

DocuFlow est une plateforme open source d'extraction, de validation humaine et d'export de données documentaires, fondée sur l'OCR et l'intelligence artificielle. Son objectif : transformer des documents en données structurées, traçables et prêtes à être utilisées dans d'autres applications.

> **Statut : en cours de développement — première version fonctionnelle.**  
> L'extraction par règles, les contrôles métier, l'interface de validation et les exports sont disponibles. Les instructions d'installation complètes seront ajoutées avec la première version publiable.

---

## Pourquoi DocuFlow ?

Les factures et formulaires contiennent des informations utiles, souvent ressaisies manuellement dans des applications métiers. DocuFlow vise à faciliter ce travail en combinant :

- extraction automatique des informations ;
- contrôles de cohérence ;
- vérification et correction par un utilisateur ;
- export dans des formats exploitables ;
- conservation de la provenance et des corrections.

---

## Fonctionnement prévu

1. Importer un document PDF ou une image.
2. Extraire les champs selon un schéma défini.
3. Afficher le document et les valeurs extraites côte à côte.
4. Présenter les sources et les anomalies détectées.
5. Corriger et valider les informations.
6. Exporter les données en JSON ou CSV.

Lorsqu'une information est absente, elle reste vide. Les valeurs extraites, déduites et corrigées sont distinguées.

---

## Première version : factures fournisseurs

Le premier cas d'application concerne les factures fournisseurs en français, avec des documents fictifs de démonstration, notamment en FCFA.

### Champs ciblés

| Groupe | Informations |
|---|---|
| Identification | Numéro de facture, date, fournisseur |
| Destinataire | Nom du client |
| Montants | Total hors taxes, taxes, total à payer |
| Paiement | Devise, échéance si présente |
| Provenance | Page, extrait et zone du document lorsque disponibles |

L'extraction des lignes d'articles est prévue dans une étape ultérieure.

### Fonctionnalités prévues

- Importation de PDF, JPEG et PNG.
- Traitement d'une facture par import.
- Extraction des champs principaux.
- Contrôles de cohérence des montants et des dates.
- Interface de correction et de validation.
- Historique des valeurs initiales et des corrections.
- Export JSON et CSV.

La localisation d'un champ est affichée uniquement lorsqu'elle peut être établie. Une localisation indisponible est signalée explicitement.

---

## Méthodes d'extraction

DocuFlow propose une interface commune pour comparer deux approches :

| Approche | Principe |
|---|---|
| Classique | Texte natif du PDF ou OCR, puis extraction par règles |
| Multimodale | Analyse des images de pages par un modèle produisant une sortie structurée |

Les deux méthodes produisent le même schéma de données, ce qui facilite leur comparaison et leur remplacement. Le choix des moteurs et fournisseurs reste à confirmer.

---

## Architecture

| Composant | Technologie | Responsabilité |
|---|---|---|
| Frontend | Next.js | Importation, consultation et validation des documents |
| API | FastAPI (Python 3.12) | API, orchestration et exports |
| Worker | Python 3.12 | Traitements documentaires en arrière-plan |
| Base de données | PostgreSQL 18 | Métadonnées, résultats et historique des corrections |
| Stockage de fichiers | Volume local | Documents originaux et images des pages |
| Environnement | Docker Compose | Développement local et déploiement |

L'architecture initiale privilégie un monolithe modulaire accompagné d'un worker. Le dépôt est organisé en monorepo :

```
apps/backend/   → API FastAPI et worker Python
apps/web/       → Frontend Next.js
benchmarks/     → Scripts d'évaluation et résultats
examples/       → Documents fictifs et annotations
docs/           → Architecture, installation et contribution
compose.yaml    → Services locaux
```

---

## Traçabilité et traitement des données

Chaque extraction conserve :

- la référence du document original ;
- le moteur utilisé et sa version ;
- la configuration ou le prompt employé ;
- les valeurs initialement extraites ;
- les corrections et la validation humaine.

Le mode de traitement précise si les documents restent sur l'infrastructure locale ou sont transmis à un fournisseur externe.

Les documents de démonstration sont fictifs. **Ne publiez pas de documents confidentiels, de clés API ou d'identifiants dans le dépôt ou les issues.**

---

## Évaluation

Un jeu de documents fictifs annotés permettra de comparer les méthodes sur des mises en page et qualités d'image variées.

Les mesures prévues :

- exactitude par champ après normalisation ;
- nombre de valeurs renseignées sans preuve dans le document ;
- proportion de factures entièrement correctes ;
- temps de traitement et coût par document ;
- nombre de corrections nécessaires ;
- qualité de la localisation des champs.

Les résultats seront accompagnés du protocole d'évaluation, des versions utilisées et d'une analyse des erreurs.

---

## Feuille de route

- [ ] Définir le schéma des champs et les critères d'acceptation.
- [x] Créer les factures fictives et leurs annotations.
- [x] Structurer le dépôt et l'environnement de développement.
- [x] Implémenter l'extraction de référence.
- [x] Ajouter les contrôles métier.
- [x] Développer l'interface de validation.
- [x] Ajouter l'export JSON et CSV.
- [ ] Intégrer une méthode multimodale.
- [ ] Publier le benchmark et l'analyse des erreurs.
- [ ] Ajouter les tests et les vérifications automatiques.
- [ ] Documenter l'installation avec Docker Compose.
- [ ] Publier une première version.

---

## Perspectives

Après validation du premier cas d'application :

- extraction des lignes d'articles ;
- prise en charge de nouveaux types de documents ;
- traitement par lots ;
- schémas d'extraction configurables ;
- connecteurs vers des applications métiers ;
- prise en charge d'autres langues.

---

## Installation

Aucune procédure d'installation exécutable n'est disponible à ce stade. Elle sera publiée avec la première implémentation.

---

## Contribution

Les contributions peuvent porter sur le développement, les données fictives, l'évaluation, l'interface et la documentation.

Avant de commencer, ouvrez une issue ou commentez une issue existante pour préciser la proposition et coordonner le travail. Chaque contribution doit expliquer les changements réalisés, leur validation et leurs éventuelles limites.

---

## Licence

DocuFlow est distribué sous licence **MIT**.

Voir le fichier [`LICENSE`](LICENSE) pour le texte complet.

---

## Auteur

**Thierry N'DRI**

- GitHub : [thiers225](https://github.com/thiers225)
- LinkedIn : [thierry-ndri](https://www.linkedin.com/in/thierry-ndri/)
- Portfolio : [thierryndri.com](https://thierryndri.com)
