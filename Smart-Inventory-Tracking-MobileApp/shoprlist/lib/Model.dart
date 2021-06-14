import 'package:firebase_database/firebase_database.dart';

class ShopItem {
  String title;
  int amount;

  ShopItem(this.title, this.amount);

  ShopItem.fromSnapShot(DataSnapshot snapshot) :
  title = snapshot.key,
  amount = snapshot.value;
}
