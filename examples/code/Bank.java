public class Bank {

	private int id;
	private String name;
	private String address;
	private Customer customer;
	private Teller teller;

	public int getId() {
 		return this.id; 
	}

	public void setId(int id) {
 		this.id = id; 
	}

	public String getName() {
 		return this.name; 
	}

	public void setName(String name) {
 		this.name = name; 
	}

	public String getAddress() {
 		return this.address; 
	}

	public void setAddress(String address) {
 		this.address = address; 
	}

	public Customer getCustomer() {
 		return this.customer; 
	}

	public void setCustomer(Customer customer) {
 		this.customer = customer; 
	}

	public Teller getTeller() {
 		return this.teller; 
	}

	public void setTeller(Teller teller) {
 		this.teller = teller; 
	}

}
