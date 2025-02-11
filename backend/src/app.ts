import express from 'express';
import cors from 'cors';
import api from './routes/api';
import passport from 'passport';
import { authorizeRequest } from './middlewares/authorizeRequest';
/* import "./passport"; */

const allowedOrigins = ['http://localhost:3000'];

const app = express();

app.use(
  cors({
    origin: function (origin, callback) {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true
  })
);
app.use(authorizeRequest);
app.use(express.json());
app.use(passport.initialize());
app.use('/v1', api);

export default app;
