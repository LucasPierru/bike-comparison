import { Request, Response } from 'express';
import Bike from '../../models/bike.mongo';
import BikeComponent from '../../models/bikeComponent.mongo';
import { Types } from 'mongoose';

export const httpGetBikes = async (req: Request, res: Response) => {
  const { perPage, page, search, type, minPrice, maxPrice } = req.query;

  const perPageNum = Number(perPage) || 10;
  const pageNum = Number(page) || 0;

  const query: any = {
    currentPrice: { $gte: minPrice || 0, $lte: maxPrice || 50000 }
  };

  if (type) {
    query.type = type;
  }

  if (search) {
    query.$text = { $search: search as string };
  }

  try {
    const bikes = await Bike.find(query)
      .limit(perPageNum)
      .skip(pageNum * perPageNum)
      .populate('brand');
    res.status(200).json({ bikes, error: null });
  } catch (error) {
    res.status(500).json({ bikes: null, error });
  }
};

export const httpGetBike = async (req: Request, res: Response) => {
  const { id } = req.params;
  const bikeId = new Types.ObjectId(id);

  try {
    const bikeComponents = await BikeComponent.find({
      bike: bikeId
    })
      .populate({
        path: 'component',
        populate: {
          path: 'brand'
        }
      })
      .populate({
        path: 'bike',
        populate: {
          path: 'brand'
        }
      });
    const components = bikeComponents.map(
      (bikeComponent) => bikeComponent.component
    );
    const bike = bikeComponents[0].toObject().bike;
    res.status(200).json({ bike: { ...bike, components }, error: null });
  } catch (error) {
    console.log(error);
    res.status(500).json({ bike: null, error });
  }
};

export const httpGetBikeTypes = async (req: Request, res: Response) => {
  try {
    const bikeTypes = await Bike.distinct('type');
    res.status(200).json({ bikeTypes, error: null });
  } catch (error) {
    console.log(error);
    res.status(500).json({ bikeTypes: null, error });
  }
};
