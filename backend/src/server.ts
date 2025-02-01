import { createServer } from "http";
import app from "./app";
import { mongoConnect } from "./services/mongo";

const server = createServer(app);

const startServer = async () => {
  await mongoConnect();

  app.get("/", (req, res) => {
    res.send("Hello World!");
  });

  server.listen(4000, () => {
    console.log(`Server running in 4000`);
  });
};

startServer();
