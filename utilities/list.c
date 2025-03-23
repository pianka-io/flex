#include <stdlib.h>
#include "list.h"

void list_insert(struct List **head, void *data) {
    struct List *node = malloc(sizeof(struct List));
    if (!node) {
        free(data);
        return;
    }
    node->data = data;
    node->next = *head;
    *head = node;
}

void list_destroy(struct List **head) {
    if (head == NULL) return;
    if (*head == NULL) return;

    struct List *node = *head;
    while (node != NULL) {
      struct List *next = node->next;
      free(node->data);
      free(node);
      node = next;
    }
    *head = NULL;
}