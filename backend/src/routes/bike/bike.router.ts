import express from 'express';
import { httpGetBike, httpGetBikes } from './bike.controller';

const bikeRouter = express.Router();

bikeRouter.get('/', httpGetBikes);
bikeRouter.get('/details/:id', httpGetBike);

export default bikeRouter;
