# 🛫 AirAlert Architecture Documentation

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        GForm["📋 Google Form<br/>(User Signups)"]
        GSheet["📊 Google Sheet<br/>(Destinations & Thresholds)"]
    end
    
    subgraph "AirAlert Core"
        DataMgr["📦 DataManager<br/>(Manages Sheet Data)"]
        FlightSearch["🔍 FlightSearch<br/>(Amadeus API)"]
        FlightData["📈 FlightData<br/>(Parse Results)"]
        Main["🎯 Main Logic<br/>(Orchestrator)"]
    end
    
    subgraph "External APIs"
        Amadeus["✈️ Amadeus Flight API<br/>(OAuth2)"]
        Sheety["🔗 Sheety API<br/>(Sheet Wrapper)"]
    end
    
    subgraph "Notification Channels"
        Email["📧 SMTP/Gmail<br/>(Email Alerts)"]
        WhatsApp["💬 Twilio API<br/>(WhatsApp Alerts)"]
    end
    
    subgraph "Users"
        Traveler["👤 Travelers"]
    end
    
    GForm -->|collects| DataMgr
    GSheet -->|stores| DataMgr
    DataMgr <-->|reads/writes| Sheety
    Sheety <-->|manages| GSheet
    Main -->|queries| FlightSearch
    FlightSearch -->|OAuth Token| Amadeus
    Amadeus -->|flight offers| FlightSearch
    FlightSearch -->|parses| FlightData
    FlightData -->|deal details| Main
    Main -->|cheapest flights| Email
    Main -->|cheapest flights| WhatsApp
    Email -->|alerts| Traveler
    WhatsApp -->|alerts| Traveler
    
    style Main fill:#ff9999
    style DataMgr fill:#99ccff
    style FlightSearch fill:#99ff99
    style Email fill:#ffcc99
    style WhatsApp fill:#ffcc99
```

## 2. Detailed Data Flow & Process

```mermaid
flowchart LR
    Start(["🚀 Start main.py"]) --> Init["⚙️ Initialize<br/>- DataManager<br/>- FlightSearch<br/>- NotificationManager"]
    
    Init --> FetchDest["📥 Fetch Destinations<br/>from Google Sheet"]
    FetchDest --> FillCodes["🔄 Auto-fill missing<br/>IATA codes"]
    
    FillCodes --> FetchUsers["📥 Fetch Customer<br/>Emails from Sheet"]
    FetchUsers --> GroupByOrigin["📊 Group Users<br/>by Origin Airport"]
    
    GroupByOrigin --> ForEachOrigin["🔁 Loop: Each Origin"]
    
    ForEachOrigin --> ForEachDest["🔁 Loop: Each Destination"]
    
    ForEachDest --> SearchDirect["✈️ Search Direct Flights"]
    SearchDirect --> SearchIndirect["✈️ Search Indirect Flights"]
    
    SearchIndirect --> GetCheapest["💰 Extract Cheapest<br/>from Both Results"]
    
    GetCheapest --> CheckPrice{{"Price <br/>Threshold?"}}
    
    CheckPrice -->|Yes| Format["📝 Format Alert Message"]
    CheckPrice -->|No| SkipDest["⏭️ Skip to<br/>Next Destination"]
    
    Format --> SendEmail["📧 Send Email<br/>to Users"]
    SendEmail --> SendWhatsApp["💬 Send WhatsApp<br/>Message"]
    
    SendWhatsApp --> LoopControl{"More<br/>Destinations?"}
    LoopControl -->|Yes| ForEachDest
    LoopControl -->|No| LoopOriginControl{"More<br/>Origins?"}
    
    SkipDest --> LoopControl
    
    LoopOriginControl -->|Yes| ForEachOrigin
    LoopOriginControl -->|No| End(["✅ Complete"])
    
    style Start fill:#ccffcc
    style End fill:#ccffcc
    style CheckPrice fill:#ffcccc
    style SendEmail fill:#ffffcc
    style SendWhatsApp fill:#ffffcc
```

## 3. Component Interaction Diagram

```mermaid
graph TB
    subgraph "Module Responsibilities"
        DM["<b>DataManager</b><br/>━━━━━━━━━━━━<br/>✓ get_destination_data()<br/>✓ update_destination_codes()<br/>✓ get_customer_emails()"]
        
        FS["<b>FlightSearch</b><br/>━━━━━━━━━━━━<br/>✓ get_token() - OAuth2<br/>✓ get_destination_code()<br/>✓ search_flights()<br/>for direct & indirect"]
        
        FD["<b>FlightData</b><br/>━━━━━━━━━━━━<br/>✓ find_cheapest_flight()<br/>extracts lowest price<br/>from API results"]
        
        NM["<b>NotificationManager</b><br/>━━━━━━━━━━━━<br/>✓ send_emails()<br/>✓ send_whatsapp()"]
        
        M["<b>Main</b><br/>━━━━━━━━━━━━<br/>✓ build_users_by_origin()<br/>✓ format_message()<br/>✓ best_of_direct_and_indirect()<br/>✓ Main flow orchestration"]
    end
    
    M -->|reads destinations| DM
    M -->|reads user emails| DM
    M -->|queries flights| FS
    FS -->|parses results| FD
    FD -->|returns FlightData| M
    M -->|triggers| NM
    
    style DM fill:#e1f5ff
    style FS fill:#e8f5e9
    style FD fill:#fff3e0
    style NM fill:#fce4ec
    style M fill:#f3e5f5
```

## 4. API Integration Points

```mermaid
graph LR
    App["🐍 AirAlert App"]
    
    subgraph "Google Ecosystem"
        GF["Google Forms<br/>(User Input)"]
        GS["Google Sheets<br/>(Data Storage)"]
    end
    
    subgraph "Flight Data"
        AM["Amadeus API<br/>(Flight Offers)"]
    end
    
    subgraph "Data Layer"
        ST["Sheety API<br/>(Wrapper)"]
    end
    
    subgraph "Notifications"
        SMTP["SMTP/Gmail<br/>(Email)"]
        TW["Twilio API<br/>(WhatsApp)"]
    end
    
    App <-->|HTTPBasicAuth| ST
    ST <-->|REST| GS
    GF -->|auto-sync| GS
    App -->|Bearer Token<br/>OAuth2| AM
    AM -->|flight offers| App
    App -->|smtplib<br/>ssl| SMTP
    App -->|Twilio SDK| TW
    
    style App fill:#ffebee
    style ST fill:#e3f2fd
    style AM fill:#e8f5e9
    style SMTP fill:#fff3e0
    style TW fill:#f3e5f5
```

## 5. Class & Method Structure

```mermaid
classDiagram
    class DataManager {
        - _user: str
        - _password: str
        - prices_endpoint: str
        - users_endpoint: str
        - destination_data: dict
        - customer_data: dict
        + get_destination_data() dict
        + update_destination_codes() void
        + get_customer_emails() list
    }
    
    class FlightSearch {
        - token: str
        + get_token() str
        + get_destination_code(city) str
        + search_flights(origin, dest, dep, ret) list
    }
    
    class FlightData {
        - price: float
        - origin_airport: str
        - destination_airport: str
        - out_date: str
        - return_date: str
        - stops: int
    }
    
    class NotificationManager {
        - smtp_address: str
        - email: str
        - email_password: str
        - twilio_verified_number: str
        - whatsapp_number: str
        - client: Client
        + send_emails(email_list, body) void
        + send_whatsapp(message) void
    }
    
    class Main {
        + build_users_by_origin(rows) dict
        + format_message(cheapest) str
        + best_of_direct_and_indirect() FlightData
    }
    
    Main --> DataManager
    Main --> FlightSearch
    Main --> FlightData
    Main --> NotificationManager
    FlightSearch --> FlightData
```

## 6. Decision & Filtering Logic

```mermaid
graph TD
    A["Get Cheapest Flight<br/>(Direct or Indirect)"] --> B{"Price Exists<br/>& Less than<br/>Threshold?"}
    
    B -->|❌ No| C["⏭️ Skip this route<br/>Don't send alert"]
    B -->|✅ Yes| D["✉️ Format Message<br/>with flight details"]
    
    D --> E["Create Alert with:<br/>• Price<br/>• Route<br/>• Dates<br/>• Stops"]
    
    E --> F["📧 Send Email to<br/>All Origin-matched Users"]
    F --> G["💬 Send WhatsApp<br/>Notification"]
    G --> H["✅ Alert Delivered"]
    
    C --> I["Continue to<br/>Next Route"]
    H --> I
    
    style B fill:#ffcccc
    style C fill:#ffeeee
    style H fill:#ccffcc
```

## 🏗️ Architecture Summary

### Architecture Pattern
**Modular, event-driven Python application** with clear separation of concerns

### Key Components
1. **DataManager** - Manages all Google Sheet interactions via Sheety API
2. **FlightSearch** - Handles Amadeus API authentication & flight queries  
3. **FlightData** - Simple data class for flight information
4. **NotificationManager** - Sends alerts via SMTP & Twilio
5. **Main** - Orchestrates the entire workflow

### Data Flow
- Google Forms → Google Sheets → Sheety API → DataManager
- DataManager queries Amadeus API via FlightSearch
- FlightData extracts best prices
- NotificationManager sends alerts via Email & WhatsApp

### Workflow Steps
1. Load destinations & customer emails from Google Sheets
2. For each user origin → search all destinations
3. Compare direct vs indirect flights via Amadeus API
4. If price < threshold → send alerts via email and WhatsApp
5. Rate limiting (2-second delays) to avoid API throttling

### External Dependencies
- **Amadeus Flight API** - Flight data and search
- **Sheety API** - Google Sheets wrapper
- **Twilio API** - WhatsApp notifications
- **SMTP/Gmail** - Email notifications
- **Google Forms & Sheets** - User data collection