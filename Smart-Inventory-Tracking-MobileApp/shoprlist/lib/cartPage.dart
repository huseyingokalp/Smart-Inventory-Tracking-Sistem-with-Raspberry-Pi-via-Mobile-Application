import 'package:flutter/material.dart';
import 'Model.dart';


class ListTileItems extends StatefulWidget {
  ShopItem cartItem;

  ListTileItems({this.cartItem});

  @override
  _ListTileItemsState createState() => _ListTileItemsState();
}

class _ListTileItemsState extends State<ListTileItems> {
  int itemCount = 0;

  @override
  Widget build(BuildContext context) {

    return new ListTile(

      title: new Text(widget.cartItem.title),
      trailing: new Row(
        children: <Widget>[
          itemCount != 0 ?

          new IconButton(
            icon: new Icon(Icons.remove),
            onPressed: () => setState(() {
              itemCount--;
              widget.cartItem.amount--;
            }),
          )

          : new Container(), new Text(itemCount.toString()),

          new IconButton(
            icon: new Icon(Icons.add),
            onPressed: () => setState(() {
              itemCount++;
              widget.cartItem.amount++;
            })
          )

        ],
        mainAxisSize: MainAxisSize.min,
      ),

    );
  }
}