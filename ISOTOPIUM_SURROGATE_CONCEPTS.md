# ISOTOPIUM & SURROGATE.TV CONCEPTS FOR AR SANDBOX RC

## PROJECT INSPIRATION

Based on research into Isotopium: Chernobyl and Surrogate.tv's construction truck live stream, we can implement similar concepts for the AR Sandbox RC project to create an engaging, interactive physical gaming experience.

## ISOTOPIUM: CHERNOBYL CONCEPT

### Overview

**Isotopium: Chernobyl** is the world's first "Remote Reality" game where players control real RC robots via the internet in a scale model of Chernobyl/Pripyat.

### Key Features

- **Real Physical Environment** - Scale model of Chernobyl exclusion zone

- **Remote Control Robots** - Real RC tanks and vehicles controlled via web browser

- **Live Video Streaming** - Multiple camera angles showing real-time action

- **Online Multiplayer** - Players from around the world compete simultaneously

- **Objective-Based Gameplay** - Collect energy items, survive, eliminate competitors

- **Real-World Physics** - Actual physical interactions and collisions

### Technical Implementation

- **WebSocket Communication** - Real-time control commands from browser to robots

- **Live Video Streaming** - Multiple IP cameras with low-latency streaming

- **Robot Fleet Management** - Multiple RC vehicles with unique capabilities

- **Collision Detection** - Physical interactions between robots and environment

- **Scoring System** - Real-time tracking of objectives and player performance

## SURROGATE.TV CONSTRUCTION CONCEPT

### Overview

Surrogate.tv created an interactive live stream where viewers could remotely control construction equipment (dump trucks and backhoes) to move balls from one side of a room to another, depositing them into hoppers for scoring.

### Key Features

- **Construction Equipment** - Real dump trucks and backhoes (RC or full-size)

- **Ball Collection Game** - Move colored balls from source to scoring hoppers

- **Automated Scoring** - Sensors detect balls entering hoppers and update scores

- **Ball Recycling System** - Automatic return of balls to playing field

- **Live Streaming** - Real-time video feed of construction site

- **Viewer Interaction** - Chat commands or interface controls for equipment

### Technical Implementation

- **Ball Detection System** - Computer vision or sensors to track ball movement

- **Hopper Sensors** - Infrared, weight, or optical sensors to detect ball entry

- **Scoring Display** - Real-time score updates on screen overlay

- **Ball Recycling** - Automated system to return balls to starting positions

- **Equipment Control** - Remote control interface for construction vehicles

## IMPLEMENTATION FOR AR SANDBOX RC

### Physical Setup

```

┌─────────────────────────────────────────────────────────┐
│                    AR SANDBOX ARENA                     │
│  ┌─────────┐    ┌──────────────┐    ┌─────────────┐    │
│  │ Ball    │    │   Sandbox    │    │   Scoring   │    │
│  │ Source  │    │   Terrain    │    │   Hoppers   │    │
│  │ Hopper  │    │              │    │             │    │
│  └─────────┘    └──────────────┘    └─────────────┘    │
│       │               │                      │          │
│       ▼               ▼                      ▼          │
│  Ball Dispenser   RC Vehicles          Ball Counters    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Camera System                      │   │
│  │  Overhead + Side Cameras for Live Streaming    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

```

### Core Components

#### 1. RC Construction Vehicle Fleet

- **Excavators** - Dig terrain, move balls with bucket

- **Dump Trucks** - Transport multiple balls at once

- **Bulldozers** - Push balls and modify terrain

- **Cranes** - Precise ball placement and lifting

#### 2. Ball Management System

- **Ball Dispensers** - Automated release of colored balls onto playing field

- **Ball Detection** - Computer vision tracking of ball positions

- **Scoring Hoppers** - Multiple hoppers with different point values

- **Recycling System** - Pneumatic or mechanical return of balls to dispensers

#### 3. Terrain Integration

- **AR Sandbox** - Real sand with depth sensing and projection

- **Terrain Modification** - Vehicles can actually dig and move sand

- **Topographic Overlay** - Real-time contour lines and elevation display

- **Construction Challenges** - Build roads, dams, foundations for bonus points

#### 4. Scoring & Gamification

- **Ball Colors** - Different colored balls worth different points

- **Time Challenges** - Limited time rounds for urgency

- **Construction Objectives** - Bonus points for building specific structures

- **Efficiency Scoring** - Points for fuel usage, time, precision

- **Multiplayer Competition** - Multiple players controlling different vehicles

### Technical Architecture

#### Hardware Components

```

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RC Vehicles   │    │   Ball System   │    │  Sensor Array   │
│                 │    │                 │    │                 │
│ • Excavators    │    │ • Dispensers    │    │ • Kinect v1     │
│ • Dump Trucks   │    │ • Hoppers       │    │ • Webcams       │
│ • Bulldozers    │    │ • Recycling     │    │ • IR Sensors    │
│ • Cranes        │    │ • Ball Tracking │    │ • Weight Sensors│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTROL SYSTEM                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Arduino   │  │ Raspberry   │  │   Computer  │            │
│  │   Control   │  │     Pi      │  │   Vision    │            │
│  │             │  │             │  │             │            │
│  │ • Vehicle   │  │ • Streaming │  │ • Ball      │            │
│  │   Control   │  │ • Sensors   │  │   Tracking  │            │
│  │ • Servos    │  │ • WiFi      │  │ • Scoring   │            │
│  │ • Motors    │  │ • Camera    │  │ • Display   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WEB INTERFACE                                │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Live      │  │   Control   │  │   Scoring   │            │
│  │  Streaming  │  │  Interface  │  │   Display   │            │
│  │             │  │             │  │             │            │
│  │ • Multiple  │  │ • Vehicle   │  │ • Real-time │            │
│  │   Cameras   │  │   Controls  │  │   Scores    │            │
│  │ • Low       │  │ • Joystick  │  │ • Leader    │            │
│  │   Latency   │  │   Support   │  │   Board     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘

```

#### Software Stack

- **Frontend** - Web interface using existing AR Sandbox HTML/JS

- **Backend** - Python server with WebSocket communication

- **Computer Vision** - OpenCV for ball tracking and scoring

- **Vehicle Control** - Arduino/ESP32 for RC vehicle communication

- **Streaming** - Low-latency video streaming (WebRTC or similar)

- **Database** - Score tracking and player statistics

### Game Modes

#### 1. Construction Challenge Mode

- **Objective** - Build specific structures (roads, buildings, dams)

- **Scoring** - Points for accuracy, speed, and resource efficiency

- **Tools** - All construction vehicles available

- **Time Limit** - 10-15 minutes per round

#### 2. Ball Collection Race

- **Objective** - Move as many balls as possible to scoring hoppers

- **Scoring** - Different colored balls worth different points

- **Strategy** - Choose between speed (many low-value balls) vs precision (few high-value balls)

- **Competition** - Multiple players with different vehicles

#### 3. Terrain Modification Challenge

- **Objective** - Reshape terrain to guide water flow or create specific topography

- **Scoring** - Points for achieving target elevation profiles

- **Physics** - Real water simulation shows success/failure

- **Education** - Learn about watersheds, erosion, and civil engineering

#### 4. Collaborative Construction

- **Objective** - Multiple players work together on large projects

- **Roles** - Different vehicles have specialized functions

- **Communication** - Chat system for coordination

- **Scoring** - Team-based scoring with individual contributions

### Integration with Existing AR Sandbox RC

#### Leverage Existing Systems

- **Physics Engine** - Use existing advanced physics for realistic interactions

- **Terrain System** - Build on existing topographic visualization

- **Vehicle Fleet** - Extend existing vehicle system with RC integration

- **Mission Framework** - Adapt existing mission system for ball collection games

#### New Components to Add

- **Ball Physics** - Extend Sandboxels physics for ball interactions

- **Scoring System** - Real-time score tracking and display

- **Live Streaming** - WebRTC integration for low-latency video

- **RC Communication** - Arduino/ESP32 integration for vehicle control

- **Sensor Integration** - Hopper sensors and ball detection systems

This concept combines the best of both Isotopium's remote reality gaming and Surrogate.tv's construction equipment interaction, creating a unique educational and entertaining experience that perfectly aligns with the AR Sandbox RC project's goals.
