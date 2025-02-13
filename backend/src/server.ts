import { createServer } from 'http';
import app from './app';
import { mongoConnect } from './services/mongo';
import 'dotenv/config';

const server = createServer(app);
const PORT = process.env.PORT || 4000;

const startServer = async () => {
  await mongoConnect();

  app.get('/', (req, res) => {
    res.send('Hello World!');
  });

  server.listen(PORT as number, '0.0.0.0', () => {
    console.log(`Server running in 4000`);
  });
};

startServer();
