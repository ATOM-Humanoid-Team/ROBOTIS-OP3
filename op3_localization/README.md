# 🧭 ROBOTIS-OP3 Localization (`op3_localization`) - Technical Breakdown & R&D Roadmap

Dokumen ini membedah arsitektur, implementasi teknis, analisis limitasi akurasi, serta cetak biru pengembangan (*R&D Roadmap / PR Backlog*) untuk package **`op3_localization`** pada robot humanoid ROBOTIS-OP3 (ATOM Humanoid ROS 2).

---

## 1. 📌 Ikhtisar & Peran Arsitektur

Package `op3_localization` bertindak sebagai penyedia estimasi pose dasar (**Base Odometry & TF Broadcaster**) yang memetakan posisi dan orientasi badan robot (*pelvis / body_link*) terhadap koordinat referensi global (`world`).

```text
 ┌─────────────────────────────────────────────────────────────┐
 │            op3_walking_module (Walking Engine)              │
 └──────────────────────────────┬──────────────────────────────┘
                                │ /robotis/pelvis_pose (40 Hz)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                 op3_localization (Node)                     │
 │  ┌───────────────────────────────────────────────────────┐  │
 │  │ 1. SO(3) Quaternions: q_total = q_old ⊗ q_offset      │  │
 │  │ 2. SE(3) Projection:  Δp_new = R(q_old) · p_offset    │  │
 │  │ 3. Pose Accumulation: p_world = p_old + Δp_new        │  │
 │  └───────────────────────────────────────────────────────┘  │
 └──────────────────────┬──────────────────────▲───────────────┘
                        │                      │ /robotis/pelvis_pose_reset
                        │ Broadcast TF         │ (Reset State Machine)
                        ▼                      │
 ┌──────────────────────────────────────────┐  │ ┌───────────────────────────┐
 │          tf2_ros::TransformBroadcaster   │  └─┤ Game Controller / User    │
 │            (world ➔ body_link)           │    │ Reset Command ("reset")   │
 └──────────────────────┬───────────────────┘    └───────────────────────────┘
                        │
                        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │       RViz2 / Navigation Stack / SLAM Global Tracking       │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. 📂 Struktur File & Komponen

```text
op3_localization/
├── CMakeLists.txt              # Build configuration ROS 2 (ament_cmake)
├── package.xml                 # Metadata & dependencies manifest (format 3)
├── README.md                   # Dokumentasi teknis & analisa arsitektur
├── include/
│   └── op3_localization/
│       └── op3_localization.h # Deklarasi kelas OP3Localization & member data
└── src/
    ├── main.cpp                # Node lifecycle & 10 Hz execution loop
    └── op3_localization.cpp    # Algoritma transformasi, subscriber, & TF broadcast
```

---

## 3. ⚠️ Analisis Kritis: Mengapa Dead-Reckoning Kinematik Belum Akurat?

Saat ini, `op3_localization` menggunakan pendekatan **Open-Loop Kinematic Dead-Reckoning** murni yang mengintegrasikan kecepatan teoritis generator langkah ($\int v \, dt$). Pada robot humanoid fisik maupun simulasi berbasis kontak dinamis (Webots ODE physics), pendekatan ini memiliki limitasi signifikan:

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │               Sumber Error & Drift pada Lokalisasi Bipedal               │
 ├────────────────────────────────┬────────────────────────────────────────┤
 │ 1. Foot Slippage (Selip Kaki)  │ Karet telapak kaki mengalami selip saat │
 │                                │ fase kontak di atas rumput lapangan.   │
 ├────────────────────────────────┼────────────────────────────────────────┤
 │ 2. Backlash & Compliance       │ Fleksibilitas mekanis sendi Dynamixel   │
 │                                │ menyebabkan panjang langkah nyata <    │
 │                                │ panjang langkah teoritis model.        │
 ├────────────────────────────────┼────────────────────────────────────────┤
 │ 3. Open-Loop (Tanpa Sensor)    │ Belum memadukan sensor IMU (Gyro/Accel) │
 │                                │ atau FSR kaki, sehingga yaw drift tidak│
 │                                │ terkoreksi saat robot berbelok.        │
 ├────────────────────────────────┼────────────────────────────────────────┤
 │ 4. Zero Landmark Correction    │ Tidak ada fusi persepsi visual garis    │
 │                                │ lapangan atau tiang gawang untuk       │
 │                                │ melokalisasi diri secara absolut.      │
 └────────────────────────────────┴────────────────────────────────────────┘
```

---

## 4. 🗺️ Roadmap Pengembangan & PR Backlog (Next Improvements)

Untuk mencapai akurasi lokalisasi kelas kompetisi KRSBI / RoboCup (toleransi error $< 10\text{ cm}$), arsitektur harus ditingkatkan melalui tahapan Pull Request (PR) berikut:

```text
       [Roadmap Arsitektur Lokalisasi Humanoid ATOM]

 ┌──────────────────────────────────────────────────────────────────┐
 │ PR-1: Kinematic + IMU Extended Kalman Filter (EKF)               │
 │ • Integrasi robot_localization (fuse gyro z-rate + accel)        │
 │ • Menghilangkan yaw drift saat melangkah cepat / berputar        │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ PR-2: Stance-Foot Anchored Odometry (Contact Detection)          │
 │ • Deteksi kaki penumpu (Stance Foot vs Swing Foot via FSR/Torsi) │
 │ • Forward Kinematics dihitung dari telapak kaki yang menapak     │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ PR-3: Visual Monte Carlo Localization (MCL / Particle Filter)    │
 │ • Deteksi garis lapangan (field lines) & titik penalti via YOLO  │
 │ • Koreksi partikel posisi absolut (x, y, θ) di lapangan 9x6 m    │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ PR-4: Standard REP-105 Frame Hierarchy Compliance                │
 │ • map (MCL Global) ➔ odom (EKF Kinematik) ➔ base_footprint ➔ body│
 └──────────────────────────────────────────────────────────────────┘
```

### Rincian PR Backlog:

1. **PR-1: Kinematic-IMU EKF Fusion (`robot_localization`)**
   - Menghubungkan topik `/robotis/open_cr/imu` (atau `/robotis_op3/imu`) dengan odometri langkah kaki menggunakan node Extended Kalman Filter (`ekf_node`).
   - Mengoreksi orientasi *yaw*, *pitch*, dan *roll* secara real-time dari fusi gyrometer dan accelerometer.

2. **PR-2: Contact-State Foot Odometry (Forward Kinematics)**
   - Mengganti model kecepatan integral rata-rata dengan *stance-foot kinematic anchoring*.
   - Saat kaki kiri menapak (SSP Kiri), transform dihitung: $\mathbf{T}_{world}^{body} = \mathbf{T}_{world}^{left\_foot} \cdot \mathbf{T}_{left\_foot}^{body}$.

3. **PR-3: Visual Field Landmark Particle Filter (AMCL)**
   - Memanfaatkan kamera kepala (`/robotis_op3/camera/image_raw`) untuk mendeteksi garis putih lapangan, lingkaran tengah, dan tiang gawang.
   - Mengeliminasi drift kumulatif dengan melakukan koreksi probabilitas partikel (*Monte Carlo Localization*).

4. **PR-4: Kepatuhan Standar ROS REP-105**
   - Mengubah hierarki transform dari `world -> body_link` langsung menjadi:
     $$\text{map} \xrightarrow{\text{Visual MCL}} \text{odom} \xrightarrow{\text{EKF Fusion}} \text{base\_footprint} \xrightarrow{\text{Leg Kinematics}} \text{body\_link}$$
