constexpr int kJointCount = 6;
long joint_milliradians[kJointCount] = {0, 0, 0, 0, 0, 0};

uint8_t checksum(const String & payload) {
  uint8_t value = 0;
  for (unsigned int i = 0; i < payload.length(); ++i) {
    value ^= static_cast<uint8_t>(payload[i]);
  }
  return value;
}

void parsePacket(const String & packet) {
  if (!packet.startsWith("$") || packet.indexOf('*') < 0) {
    return;
  }

  const int star = packet.indexOf('*');
  const String payload = packet.substring(1, star);
  const String checksum_text = packet.substring(star + 1);
  const uint8_t expected = static_cast<uint8_t>(strtoul(checksum_text.c_str(), nullptr, 16));
  if (checksum(payload) != expected) {
    return;
  }
  if (!payload.startsWith("AIM,")) {
    return;
  }

  int start = 4;
  for (int joint = 0; joint < kJointCount; ++joint) {
    int comma = payload.indexOf(',', start);
    if (comma < 0 && joint < kJointCount - 1) {
      return;
    }
    const int end = comma < 0 ? payload.length() : comma;
    joint_milliradians[joint] = payload.substring(start, end).toInt();
    start = end + 1;
  }
}

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    const String packet = Serial.readStringUntil('\n');
    parsePacket(packet);
  }
}

