#ifndef FLEX_LIST_H
#define FLEX_LIST_H

struct List {
  void *data;
  struct List *next;
};

void list_insert(struct List **head, void *data);
void list_destroy(struct List **head);

#endif