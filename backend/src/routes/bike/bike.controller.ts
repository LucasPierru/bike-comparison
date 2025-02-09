import { Request, Response } from 'express';
import Bike from '../../models/bike.mongo';
import BikeComponent from '../../models/bikeComponent.mongo';
import { Types } from 'mongoose';

export const httpGetBikes = async (req: Request, res: Response) => {
  const { perPage, page, search } = req.query;

  const perPageNum = Number(perPage) || 10;
  const pageNum = Number(page) || 0;

  let bikeRequest;

  try {
    if (search) {
      bikeRequest = Bike.find({
        $text: { $search: search as string }
      });
    } else {
      bikeRequest = Bike.find({});
    }
    const bikes = await bikeRequest
      .limit(perPageNum)
      .skip(pageNum * perPageNum);
    res.status(200).json({ bikes });
  } catch (error) {
    res.status(500).json({ message: `Cannot access bikes`, error });
  }
};

export const httpGetBike = async (req: Request, res: Response) => {
  const { id } = req.params;
  const bikeId = new Types.ObjectId(id);

  try {
    const bikeComponents = await BikeComponent.find({
      bike: bikeId
    }).populate({
      path: 'component',
      populate: {
        path: 'brand'
      }
    });
    const components = bikeComponents.map(
      (bikeComponent) => bikeComponent.component
    );
    const bike = await Bike.findById(id).populate('brand');
    res.status(200).json({ ...bike?.toObject(), components });
  } catch (error) {
    console.log(error);
    res.status(500).json({ message: `Cannot access bikes`, error });
  }
};
