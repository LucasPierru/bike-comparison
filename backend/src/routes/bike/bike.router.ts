import express from 'express';
import { httpGetBike, httpGetBikes, httpGetBikeTypes } from './bike.controller';

const bikeRouter = express.Router();

bikeRouter.get('/', httpGetBikes);
bikeRouter.get('/details/:id', httpGetBike);
bikeRouter.get('/types', httpGetBikeTypes);

export default bikeRouter;
