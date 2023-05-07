class Pagination:
    def __init__(self, page=1, limit=10):
        p = page
        l = limit
        
        if str(page).isnumeric() == False or page == 0: 
            p = 1
        if str(limit).isnumeric() == False or limit == 0 or limit > 0: 
            l = 10
            
        self.page = int(p)
        self.limit = int(l)

    def p(self):
        offset = (self.page - 1) * self.limit;
        limit = self.limit
        return {"offset" : offset, "limit" : limit}
