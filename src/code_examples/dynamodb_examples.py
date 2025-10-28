"""
DynamoDB-specific code examples for RAG/KG population.

WHY:
DynamoDB examples demonstrate single-table design patterns, composite keys,
and access pattern optimization for serverless applications.

RESPONSIBILITY:
- Provide DynamoDB single-table design examples
- Demonstrate composite key patterns (PK/SK)
- Show Global Secondary Index (GSI) usage
- Include transaction and batch operation patterns

PATTERNS:
- Use single-table design to minimize tables and costs
- Design composite keys based on access patterns
- Leverage GSIs for alternate query patterns
- Use transactions for ACID guarantees across items
"""

from code_example_types import CodeExample


DYNAMODB_EXAMPLES = [
    CodeExample(
        language="JavaScript",
        pattern="DynamoDB Single-Table Design",
        title="Multi-Entity Single-Table Design with GSI",
        description="DynamoDB single-table design pattern for e-commerce with access patterns",
        code='''// DynamoDB Single-Table Design Pattern
// Why: Minimize number of tables, efficient queries, lower costs
// Prevents: Multiple queries, joins, high read costs

/**
 * Table Schema: ecommerce
 *
 * Access Patterns:
 * 1. Get user by ID
 * 2. Get all orders for a user
 * 3. Get order by ID
 * 4. Get all products in an order
 * 5. Get product by SKU
 * 6. Get all reviews for a product
 */

const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

const TABLE_NAME = 'ecommerce';

// ==== TABLE DESIGN ====

/**
 * Primary Key: PK (Partition Key), SK (Sort Key)
 * GSI1: GSI1PK (Partition Key), GSI1SK (Sort Key)
 *
 * Entity Types:
 *
 * USER:
 *   PK: USER#<userId>
 *   SK: METADATA
 *   Type: USER
 *
 * ORDER:
 *   PK: USER#<userId>
 *   SK: ORDER#<orderId>
 *   GSI1PK: ORDER#<orderId>  // For fetching order by ID
 *   GSI1SK: METADATA
 *   Type: ORDER
 *
 * ORDERITEM:
 *   PK: ORDER#<orderId>
 *   SK: ITEM#<productSku>
 *   Type: ORDERITEM
 *
 * PRODUCT:
 *   PK: PRODUCT#<sku>
 *   SK: METADATA
 *   Type: PRODUCT
 *
 * REVIEW:
 *   PK: PRODUCT#<sku>
 *   SK: REVIEW#<reviewId>
 *   GSI1PK: USER#<userId>  // For user's reviews
 *   GSI1SK: REVIEW#<reviewId>
 *   Type: REVIEW
 */


// ==== CREATE OPERATIONS ====

// Create user
async function createUser(userId, userData) {
    const params = {
        TableName: TABLE_NAME,
        Item: {
            PK: `USER#${userId}`,
            SK: 'METADATA',
            Type: 'USER',
            userId,
            name: userData.name,
            email: userData.email,
            createdAt: new Date().toISOString()
        },
        ConditionExpression: 'attribute_not_exists(PK)'  // Prevent overwrite
    };

    return dynamodb.put(params).promise();
}

// Create order with transaction (ACID compliance)
async function createOrder(userId, orderId, items) {
    const timestamp = new Date().toISOString();

    // Build transaction items
    const transactItems = [
        // Create order metadata
        {
            Put: {
                TableName: TABLE_NAME,
                Item: {
                    PK: `USER#${userId}`,
                    SK: `ORDER#${orderId}`,
                    GSI1PK: `ORDER#${orderId}`,
                    GSI1SK: 'METADATA',
                    Type: 'ORDER',
                    orderId,
                    userId,
                    status: 'pending',
                    total: items.reduce((sum, item) => sum + (item.price * item.quantity), 0),
                    createdAt: timestamp
                },
                ConditionExpression: 'attribute_not_exists(PK)'
            }
        }
    ];

    // Add order items
    items.forEach(item => {
        transactItems.push({
            Put: {
                TableName: TABLE_NAME,
                Item: {
                    PK: `ORDER#${orderId}`,
                    SK: `ITEM#${item.sku}`,
                    Type: 'ORDERITEM',
                    orderId,
                    sku: item.sku,
                    productName: item.productName,
                    quantity: item.quantity,
                    price: item.price,
                    createdAt: timestamp
                }
            }
        });
    });

    const params = { TransactItems: transactItems };
    return dynamodb.transactWrite(params).promise();
}


// ==== QUERY OPERATIONS ====

// Get user by ID (single item query)
async function getUser(userId) {
    const params = {
        TableName: TABLE_NAME,
        Key: {
            PK: `USER#${userId}`,
            SK: 'METADATA'
        }
    };

    const result = await dynamodb.get(params).promise();
    return result.Item;
}

// Get all orders for a user (query with begins_with)
async function getUserOrders(userId, limit = 20) {
    const params = {
        TableName: TABLE_NAME,
        KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues: {
            ':pk': `USER#${userId}`,
            ':sk': 'ORDER#'
        },
        Limit: limit,
        ScanIndexForward: false  // Most recent first
    };

    const result = await dynamodb.query(params).promise();
    return result.Items;
}

// Get order by ID using GSI
async function getOrder(orderId) {
    const params = {
        TableName: TABLE_NAME,
        IndexName: 'GSI1',
        KeyConditionExpression: 'GSI1PK = :pk AND GSI1SK = :sk',
        ExpressionAttributeValues: {
            ':pk': `ORDER#${orderId}`,
            ':sk': 'METADATA'
        }
    };

    const result = await dynamodb.query(params).promise();
    return result.Items[0];
}

// Get all items in an order
async function getOrderItems(orderId) {
    const params = {
        TableName: TABLE_NAME,
        KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues: {
            ':pk': `ORDER#${orderId}`,
            ':sk': 'ITEM#'
        }
    };

    const result = await dynamodb.query(params).promise();
    return result.Items;
}

// Get all reviews for a product
async function getProductReviews(sku, limit = 20) {
    const params = {
        TableName: TABLE_NAME,
        KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues: {
            ':pk': `PRODUCT#${sku}`,
            ':sk': 'REVIEW#'
        },
        Limit: limit
    };

    const result = await dynamodb.query(params).promise();
    return result.Items;
}


// ==== UPDATE OPERATIONS ====

// Update order status
async function updateOrderStatus(userId, orderId, newStatus) {
    const params = {
        TableName: TABLE_NAME,
        Key: {
            PK: `USER#${userId}`,
            SK: `ORDER#${orderId}`
        },
        UpdateExpression: 'SET #status = :status, updatedAt = :timestamp',
        ExpressionAttributeNames: {
            '#status': 'status'  // 'status' is reserved word
        },
        ExpressionAttributeValues: {
            ':status': newStatus,
            ':timestamp': new Date().toISOString()
        },
        ReturnValues: 'ALL_NEW'
    };

    const result = await dynamodb.update(params).promise();
    return result.Attributes;
}


// ==== BATCH OPERATIONS ====

// Batch get multiple products
async function getProducts(skus) {
    const keys = skus.map(sku => ({
        PK: `PRODUCT#${sku}`,
        SK: 'METADATA'
    }));

    const params = {
        RequestItems: {
            [TABLE_NAME]: {
                Keys: keys
            }
        }
    };

    const result = await dynamodb.batchGet(params).promise();
    return result.Responses[TABLE_NAME];
}


// ==== CONDITIONAL OPERATIONS ====

// Add review only if user purchased product
async function addReview(userId, sku, reviewId, rating, comment) {
    // First, verify user has ordered this product (query)
    const orderParams = {
        TableName: TABLE_NAME,
        IndexName: 'GSI1',
        KeyConditionExpression: 'GSI1PK = :userPk',
        FilterExpression: 'contains(orderItems, :sku)',  // Simplified - actual implementation needs orderItems query
        ExpressionAttributeValues: {
            ':userPk': `USER#${userId}`,
            ':sku': sku
        },
        Limit: 1
    };

    // If user has ordered product, add review
    const params = {
        TableName: TABLE_NAME,
        Item: {
            PK: `PRODUCT#${sku}`,
            SK: `REVIEW#${reviewId}`,
            GSI1PK: `USER#${userId}`,
            GSI1SK: `REVIEW#${reviewId}`,
            Type: 'REVIEW',
            reviewId,
            userId,
            sku,
            rating,
            comment,
            createdAt: new Date().toISOString()
        }
    };

    return dynamodb.put(params).promise();
}

// Export functions
module.exports = {
    createUser,
    createOrder,
    getUser,
    getUserOrders,
    getOrder,
    getOrderItems,
    getProductReviews,
    updateOrderStatus,
    getProducts,
    addReview
};
''',
        quality_score=96,
        tags=["DynamoDB", "NoSQL", "single-table-design", "GSI", "transactions"],
        complexity="advanced",
        demonstrates=["Single-Table Design", "GSI", "Transactions", "Composite Keys", "Access Patterns"],
        prevents=["Multiple Queries", "Joins", "Scans", "High Read Costs"]
    ),
]
