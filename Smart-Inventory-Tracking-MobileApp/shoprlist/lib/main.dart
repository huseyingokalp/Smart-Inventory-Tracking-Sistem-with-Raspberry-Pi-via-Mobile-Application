import 'package:flutter/material.dart';
import 'package:shoprlist/ShoppingListPage.dart';


void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {

  @override
  Widget build(BuildContext context) {

    return MaterialApp(
      title: 'Welcome to Flutter',
      theme: ThemeData(
        primarySwatch: Colors.red,
      ),

      home: ShopingList(),
    );
  }
}


