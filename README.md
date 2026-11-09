
## Last Robot Standing

Last Robot Standing is a simple robot elimination game involving three robots: **Wall-E, BumbleBee, and Optimus Prime**.

### How It Works

1. **Docker Services:** The application runs six services using Docker Compose:
   - Control Service
   - Kafka Broker
   - Kafka UI (for monitoring)
   - Three Robot Services (one for each robot)

2. **Game Initialization:** The Control Service starts the game by randomly shuffling the three robots and publishing their names to a Kafka topic.

3. **Message Distribution:** Kafka makes the message available to all three robots.

4. **Turn Selection:** Each robot checks whether its name is first on the list.

5. **Elimination:** The selected robot announces its position, removes itself from the list, reshuffles the remaining robots, and publishes the updated list back to Kafka.

6. **Winner:** The process repeats until only one robot remains, who is declared the winner.
